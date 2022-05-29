import flask
import flask_login
import database
# Imports for recovery
# import random
# import yagmail
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = flask.Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if not database.check_user_exists(email):
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if not database.check_user_exists(email):
        return

    user = User()
    user.id = email
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')

    email = flask.request.form['email']
    password = flask.request.form['password']
    if database.verify_email_and_password(email, password):
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))
    return 'Bad login'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if flask.request.method == 'GET':
        return flask.render_template('signup.html')

    email = flask.request.form['email']
    password = flask.request.form['password']
    password_conf = flask.request.form['password-confirmation']
    if password != password_conf:
        return 'Passwords do not match'
    if database.verify_email_and_password(email, password):
        return 'User already exists'
    database.add_user_to_database(email, None, password, None)
    user = User()
    user.id = email
    flask_login.login_user(user)
    return flask.redirect(flask.url_for('protected'))

@app.route('/recover', methods=['GET'])
def recover():
    return flask.render_template('recover.html')

@app.route('/protected')
@flask_login.login_required
def protected():
    # return 'Logged in as: ' + flask_login.current_user.id
    user_email = flask_login.current_user.id
    user_username, user_password, user_base_url = database.get_user_from_database(user_email)
    user_term = database.get_term_from_database(user_email)
    return flask.render_template('protected.html', user_email=user_email, user_username=user_username, user_base_url=user_base_url, user_term=user_term)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))

@app.route('/')
def root():
    return homepage()

@app.route('/index', methods=['GET'])
def index():
    return homepage()

def homepage():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('protected'))
    return flask.render_template('index.html')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401

# ---------------------------------------------------------------------------- #
#                                 User actions                                 #
# ---------------------------------------------------------------------------- #
def flash_alert(message, category):
    alert = flask.Markup('<div class="alert alert-{} alert-dismissible fade show" role="alert">{}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>'.format(category, message))
    return flask.flash(alert)

def render_protected():
    user_email = flask_login.current_user.id
    user_username, user_password, user_base_url = database.get_user_from_database(user_email)
    user_term = database.get_term_from_database(user_email)
    return flask.render_template('protected.html', user_email=user_email, user_username=user_username, user_base_url=user_base_url, user_term=user_term)

@app.route('/set_user_info', methods=['POST'])
def set_user_info():
    user_email = flask_login.current_user.id
    user_name = flask.request.form['username']
    user_base_url = flask.request.form['base_url']
    database.set_user_info(user_email, user_name, user_base_url)
    # Flash bootstrap alert
    flash_alert('User info updated', 'success')
    return render_protected()

@app.route('/set_term', methods=['POST'])
def set_term():
    user_email = flask_login.current_user.id
    term = flask.request.form['term']
    # Remove the old term and add the new one
    database.delete_term_from_database(user_email)
    database.add_term_to_database(user_email, term)
    # Flash bootstrap alert
    flash_alert('Term updated', 'success')
    return render_protected()

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_email = flask_login.current_user.id
    user_password = flask.request.form['password']
    if not database.verify_email_and_password(user_email, user_password): return 'Bad password'
    database.delete_user(user_email)

    # Logout the user
    flask_login.logout_user()

    # Flash bootstrap alert
    flash_alert('User deleted', 'danger')
    return flask.render_template('index.html')


@app.route('/edit_classes', methods=['POST'])
def edit_classes():
    email = flask_login.current_user.id

    classes_form = flask.request.form.to_dict()

    # Everything else in the form is either a class or a synonym, so we need to differentiate based on the field name
    # Because each field gets a new number after the name, we check the first 10 or 13 characters of the field name to see if it starts with 
    # class_name or class_synonym.
    class_names = [classes_form[class_name] for class_name in classes_form if class_name[0:10] == "class_name"] # Get all the class names from their keys
    # Get all the class synonyms from their keys and use split to make them a list
    class_synonyms = [classes_form[class_synonym].split(',') for class_synonym in classes_form if class_synonym[0:13] == "class_synonym"]
    classes = dict(zip(class_names, class_synonyms))

    # This replaces the old classes with the new ones, so we need to delete the old ones
    database.remove_classes_from_database(email)
    database.add_classes_to_database(email, classes) # Add the new classes to the database
    flash_alert('Classes updated', 'success')
    return render_protected()

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = flask_login.current_user.id
    password = flask.request.form['password']
    database.set_password(email, password)
    flash_alert('Password updated', 'success')
    return render_protected()

# EMAIL_OAUTH_CREDS_PATH = 'oauth2_creds.json'
# WEB_INTERFACE_URL = '/'

# @app.route('/generate_recovery_code', methods=['POST'])
# def generate_recovery_code():
#     email = flask_login.current_user.id
#     recovery_code = random.randint(100000, 999999)
#     database.add_recovery_to_database(email, recovery_code)
#     yag = yagmail.SMTP('noreply.dashboard.api', oauth2_file=EMAIL_OAUTH_CREDS_PATH)
#     contents = [
#         "<h1>Grades Dashboard Recovery Code</h1>",
#         "Your recovery code is <code>{}</code>".format(recovery_code),
#         "Please enter this code in the password recovery form on the <a href={}>Grades Dashboard web interface</a>.".format(WEB_INTERFACE_URL),
#         "This code will eventually expire. If you don't use before it expires, you will need to generate a new code.",
#         "<br><br>Not you? Don't worry - this code will expire soon.",
#         "<br><br>Thanks for using Grades Dashboard!"
#     ]
#     yag.send(email, 'Grades Dashboard Password Reset', contents)
#     flash_alert('Recovery code generated. Check your email and enter it below.', 'primary')
#     return flask.render_template('recover.html')

# @app.route('/reset_password', methods=['POST'])
# def reset_password():
#     email = flask_login.current_user.id
#     recovery_code = flask.request.form['recovery_code']
#     new_password = flask.request.form['new_password']
#     new_password_conf = flask.request.form['new_password_conf']
#     if new_password != new_password_conf:
#         flash_alert('Passwords do not match. Please try again.', 'danger')
#         return flask.render_template('recover.html')
#     if not database.verify_recovery(email, recovery_code):
#         flash_alert('Invalid recovery code. Please try again.', 'danger')
#         return flask.render_template('recover.html')
#     database.delete_recovery_from_database(email)
#     old_user = database.get_user_from_database(email)
#     database.delete_user_from_database(email)
#     new_user = [email, old_user[1], new_password, old_user[2]]
#     database.add_user_to_database(new_user[0], new_user[1], new_user[2], new_user[3])
    
#     flash_alert('Password reset. You can now log in.', 'success')
#     return flask.render_template('login.html')

database.create_tables()

if __name__ == '__main__':
    app.run(debug=True)