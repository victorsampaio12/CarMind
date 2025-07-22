from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_user, current_user, login_required
from form.form_user import UserForm
from form.form_login import LoginForm
from models.user_model import User, db

user_bp = Blueprint('user', __name__)

def get_auth_headers():
    token = session.get('token')
    return {'Authorization': f'Bearer {token}'} if token else {}

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            complet_name=form.complet_name.data,
            email=form.email.data,
            phone=form.phone.data,
            accepted_terms=form.term_of_responsibility.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('user.register'))
    return render_template('register.html', form=form)


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('garage_bp.menu'))  
        else:
            flash('Email ou senha inválidos')

    return render_template('login.html', form=form)


@user_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    form = UserForm()

    if request.method == 'POST' and form.validate_on_submit() and form.update.data:
        current_user.complet_name = form.complet_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data

        if form.password.data:
            current_user.set_password(form.password.data)

        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for('user.perfil'))
    
    form.complet_name.data = current_user.complet_name
    form.email.data = current_user.email
    form.phone.data = current_user.phone

    return render_template('profile.html', form=form)
