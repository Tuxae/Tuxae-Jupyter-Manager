from functools import wraps
from dotenv import load_dotenv

import werkzeug.exceptions
from flask import Flask
from flask import render_template, redirect, url_for
from flask_admin import Admin
from flask_login import LoginManager
from flask_login.utils import current_user
from flask_mail import Mail

from src.admin_interface.initialize import initialize_admin
from src.db_interface.config import Config
from src.db_interface.models import initialize_db, Users, MyAdminView

load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
db = initialize_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(app, name='Tuxae Jupyter Manager', index_view=MyAdminView(url='/admin'))
initialize_admin(admin, db)


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
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    return render_template('register.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == "GET":
        return render_template('forgot-password.html')
    return render_template('forgot-password.html')


@app.errorhandler(404)
def handle_404(err: werkzeug.exceptions.NotFound):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)
