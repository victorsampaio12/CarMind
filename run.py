from flask import Flask, render_template, session, redirect, url_for
from models.user_model import db, User
from routes.user_routes import user_bp
from routes.menu_routes import garage_bp
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from form.form_user import UserForm

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = '04062019'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:04062019@localhost/carmind'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Cria login_manager e inicializa
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # nome da rota de login (ajuste se for blueprint)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/start')
def start():
    return render_template('start.html')

@app.route('/register')
def register():
    form = UserForm()
    return render_template('register.html', form=form)


app.register_blueprint(user_bp)
app.register_blueprint(garage_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
