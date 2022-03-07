from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import ValidationError, InputRequired, DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = EmailField(label=('Электронная почта'), validators=[InputRequired(), Email(), Length(max=2025)])
    password = PasswordField(label=('Пароль'), validators=[InputRequired(),
        Length(min=6, message='Password should be at least %(min)d characters long')])
    submit = SubmitField(label=('Авторизоваться'))


class CreateUserForm(FlaskForm):
    name = StringField(label=('Имя'), validators=[DataRequired(), Length(max=120)])
    surname = StringField(label=('Фамилия'), validators=[DataRequired(), Length(max=120)])
    email = EmailField(label=('Электронная почта'), validators=[DataRequired(), Email(), Length(max=2025)])
    password = PasswordField(label=('Пароль'), validators=[InputRequired()])
    old = StringField(label=('Возраст'), validators=[DataRequired(), Length(max=120)])
    work = StringField(label=('Должность и работа'), validators=[DataRequired(), Length(max=120)])
    photo = ""
    submit = SubmitField(label=('Зарегистрироваться'))

