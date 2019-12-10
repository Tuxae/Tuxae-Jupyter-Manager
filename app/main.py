from functools import wraps

import docker
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
from src.auth.register import is_fake_register_form, password_validator
from src.auth.token import check_token
from src.db_interface.config import Config
from src.db_interface.domains import check_whitelist_domain
from src.db_interface.models import initialize_db, Users, MyAdminView
from src.db_interface.users import create_user, user_exists
from src.db_interface.secret import SERVER_DOMAIN, DEFAULT_ADMIN_EMAIL
from src.docker_interface.docker import get_docker_containers, get_docker_images, check_image
from src.mail.sender import send_register_mail
from src.misc.functions import sanitize_username

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
    containers = get_docker_containers(docker_client)
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
    username = sanitize_username(current_user.username)
    try:
        environment = [
            f'VIRTUAL_HOST={username}.{SERVER_DOMAIN}',
            f'VIRTUAL_PORT=8888',
            f'LETSENCRYPT_HOST={username}.{SERVER_DOMAIN}',
            f'LETSENCRYPT_EMAIL={DEFAULT_ADMIN_EMAIL}'
        ]
        docker_client.containers.run(
            image,
            detach=True,
            environment=environment,
            volumes={
                f'/home/{username}':
                    {
                        'bind': '/home/jovyan/work',
                        'mode': 'rw'
                    }
            }
        )
        flash('Container successfully created', 'success')
    except docker.errors.ContainerError:
        flash('Container Error', 'error')
    except docker.errors.ImageNotFound:
        flash('Image not found', 'error')
    except docker.errors.APIError as e:
        flash(str(e.explanation), 'error')
    return redirect(url_for('index'))


@app.route('/containers/<string:container_id>/restart', methods=['POST'])
@login_required
def restart_container(container_id: str):
    docker_client.containers.get(container_id).start()
    return redirect(url_for('index'))


@app.route('/containers/<string:container_id>/stop', methods=['POST'])
@login_required
def stop_container(container_id: str):
    docker_client.containers.get(container_id).stop()
    return redirect(url_for('index'))


@app.route('/containers/<string:container_id>/delete', methods=['POST'])
@login_required
def delete_container(container_id: str):
    docker_client.containers.get(container_id).remove(force=True)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    if is_fake_login_form(request.form):
        flash('A wrong form has been sent.', 'error')
        return redirect(url_for('index'))
    user = get_admin_user(request.form)
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
    return render_template('forgot-password.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def handle_404(err: werkzeug.exceptions.NotFound):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)
