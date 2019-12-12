from functools import wraps

import docker.errors
import werkzeug.exceptions
from flask import Flask
from flask import render_template, redirect, url_for, request, flash
from flask_admin import Admin
from flask_login import LoginManager
from flask_login.utils import current_user, login_user, logout_user
from flask_mail import Mail

from src.admin_interface.initialize import initialize_admin
from src.auth.auth import is_fake_login_form, get_admin_user
from src.auth.form import is_fake_register_form, is_fake_reset_password_form, password_validator
from src.auth.token import check_token
from src.db_interface.config import Config
from src.db_interface.containers import associate_user_container, docker_image_already_deployed_by_user, \
    delete_association_user_container
from src.db_interface.domains import check_whitelist_domain
from src.db_interface.models import initialize_db, Users, MyAdminView
from src.db_interface.users import create_user, user_exists, update_user_token, update_user_password, get_user_by_email
from src.docker_interface.docker import get_docker_containers, get_docker_containers_ids, get_docker_images, \
    check_image, deploy_container
from src.mail.sender import send_register_mail, send_forgot_password_mail

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
db = initialize_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(app, name='Tuxae Jupyter Manager', index_view=MyAdminView(url='/admin'))
initialize_admin(admin, db)

docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/', methods=['GET'])
@login_required
def index():
    user = get_user_by_email(current_user.email)
    containers = get_docker_containers(docker_client, user)
    images = get_docker_images(docker_client)
    return render_template('index.html', containers=containers, images=images)


@app.route('/containers/create', methods=['POST'])
@login_required
def create_container():
    if list(request.form.keys()) != ['image']:
        flash('A wrong form has been sent.', 'error')
        return redirect(url_for('index'))
    image = request.form['image']
    if not check_image(image):
        #  image is not from registry
        flash('A wrong form has been sent.', 'error')
        return redirect(url_for('index'))
    user = get_user_by_email(current_user.email)
    if not current_user.is_admin and not docker_image_already_deployed_by_user(db, user, image):
        flash('You cannot run several containers from the same docker image with a non-admin account.', 'error')
        return redirect(url_for('index'))
    container = deploy_container(docker_client, image, current_user)
    associate_user_container(db, user, container, image)
    return redirect(url_for('index'))


@app.route('/containers/<string:container_id>/restart', methods=['POST'])
@login_required
def restart_container(container_id: str):
    user = get_user_by_email(current_user.email)
    containers_ids = get_docker_containers_ids(docker_client, user)
    if container_id not in containers_ids:
        flash('You do not own this container. Access forbidden.', 'error')
        return redirect(url_for('index'))
    docker_client.containers.get(container_id).start()
    return redirect(url_for('index'))


@app.route('/containers/<string:container_id>/stop', methods=['POST'])
@login_required
def stop_container(container_id: str):
    user = get_user_by_email(current_user.email)
    containers_ids = get_docker_containers_ids(docker_client, user)
    if container_id not in containers_ids:
        flash('You do not own this container. Access forbidden.', 'error')
        return redirect(url_for('index'))
    if docker_client.containers.get(container_id).status == 'running':
        docker_client.containers.get(container_id).stop()
    return redirect(url_for('index'))


@app.route('/containers/<string:container_id>/delete', methods=['POST'])
@login_required
def delete_container(container_id: str):
    user = get_user_by_email(current_user.email)
    containers_ids = get_docker_containers_ids(docker_client, user)
    if container_id not in containers_ids:
        flash('You do not own this container. Access forbidden.', 'error')
        return redirect(url_for('index'))
    container = docker_client.containers.get(container_id)
    delete_association_user_container(db, container)
    container.remove(force=True)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    if is_fake_login_form(request.form):
        flash('A wrong form has been sent.', 'error')
        return redirect(url_for('index'))
    user = get_admin_user(request.form)
    if user is None:
        flash('Invalid credentials.', 'error')
        return redirect(url_for('index'))
    if not user.is_verified:
        flash('Please verify your account before trying to login.', 'error')
        return redirect(url_for('index'))
    if user is not None:
        login_user(user)
        if user.is_admin:
            flash('You are logged in as an administrator', 'success')
        else:
            flash('Authentication successful.', 'success')
    else:
        flash('Authentication failure.', 'error')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    if is_fake_register_form(request.form):
        flash('A wrong form has been sent.', 'error')
        return redirect(url_for('register'))
    if not password_validator(request.form):
        flash('Password were different.', 'error')
        return redirect(url_for('register'))
    email, password = request.form['email'], request.form['password1']
    if not check_whitelist_domain(email):
        flash('You cannot register with this email, please use a whitelisted domain email.', 'error')
        return redirect(url_for('register'))
    if user_exists(email):
        flash('This email is already used.', 'error')
        return redirect(url_for('register'))
    new_user = create_user(db, email, password)
    send_register_mail(mail, new_user)
    flash('Your account has been created. Check your email to verify your account. Do not forget to check in SPAM as '
          'well.', 'success')
    return redirect(url_for('index'))


@app.route('/verify', methods=['GET'])
def verify():
    token = request.args.get('token')
    if token is None:
        flash('No token to check.', 'error')
        return redirect(url_for('login'))
    user = check_token(token)
    if user is None:
        flash('Token is either invalid or has expired.', 'error')
        return redirect(url_for('login'))
    user.is_verified = True
    db.session.commit()
    flash('Your account has been verified. You can login now.', 'success')
    return redirect(url_for('login'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == "GET":
        return render_template('forgot-password.html')
    if list(request.form.keys()) != ['email']:
        flash('A wrong form has been sent.', 'error')
        return redirect(url_for('index'))
    email = request.form['email']
    flash(f'A reset password link has been sent to {email} if an account exists with this email.', 'success')
    if not user_exists(email):
        return render_template('forgot-password.html')
    user = update_user_token(db, email)
    send_forgot_password_mail(mail, user)
    return render_template('forgot-password.html')


@app.route('/reset-password', methods=['GET'])
def reset_password_get():
    token = request.args.get('token')
    if token is None:
        flash('No token to check.', 'error')
        return redirect(url_for('login'))
    user = check_token(token)
    if user is None:
        flash('Token is either invalid or has expired.', 'error')
        return redirect(url_for('login'))
    if not user.is_verified:
        user.is_verified = True
    db.session.commit()
    user = update_user_token(db, user.email)
    return render_template('reset-password.html', token=user.token)


@app.route('/reset-password', methods=['POST'])
def reset_password_post():
    if is_fake_reset_password_form(request.form):
        flash('A wrong form has been sent.', 'error')
        return redirect(url_for('register'))
    if not password_validator(request.form):
        flash('Password were different.', 'error')
        return redirect(url_for('register'))
    token, password = request.form['token'], request.form['password1']
    user = check_token(token)
    if user is None:
        # Do not display if token is valid because post token has been generated by the backend (do not give info)
        flash('A wrong form has been sent.', 'error')
        return redirect(url_for('login'))
    update_user_password(db, user, password)
    flash('Your password has been successfully updated.', 'success')
    return redirect(url_for('login'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def handle_404(err: werkzeug.exceptions.NotFound):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
