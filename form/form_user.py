from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

class UserForm(FlaskForm):
    complet_name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-mail', validators=[DataRequired()])
    phone = StringField('Telefone', validators=[Length(min=0, max=20)])
    password = PasswordField('Senha', validators=[])
    repeat_password = PasswordField('Repetir Senha', validators=[])
    term_of_responsibility = BooleanField('')
    register = SubmitField('Cadastrar')
    update = SubmitField('Atualizar')


    
