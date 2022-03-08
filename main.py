import hashlib
import json
import os
import uuid
from datetime import datetime as dt
from forms import LoginForm, CreateUserForm, ChangeUserForm, SelectUserForm
from yapi import YaAPI as yap

from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user

csrf = CSRFProtect()
app = Flask(__name__)
csrf.init_app(app)

app.config['SECRET_KEY'] = 'AAAAB3NzaC1yc2EAAAADAQABAAABgQDjpNwz5lbIEPRWw2RRzsZAJNmXInOGmDsUFDRDTo7cPdLQrD7jHzgogAYh0PIxvmAnTBAUg77+lCaL3EifSfi7gd4dOnv+L2b07eVra7VuYw9cQ2amYQdpTs3bZU9k9vbDXCgZPR0xrOifrg3x2P8vZs9lHrhUhWYA70pd3ouXhV1ljftmbVqAF6JmlldCGgvPgMimMukCv/jXno2lfgi/ZSzidwngow5Ecv1jSgZja3GpO2DLf0Jyr3WcO+15/i6tHHHJf88ZJIV8sGm7m4NWE50i7Ab+eDOsgJbZyjfgyCUFJQQgsiOpjGVYm6LrtZx5a8gGnp0MHPzYdMo+7P9w0I1fv9dShcfi/kz1ekadyHjr/B+EOkfItOH7Dslzrnilp7VLyA61nKcftGy9lJOF8rn2v43kBQNDSQGvcjlUdcFJ3t6ANG3s3zBzpFCbUoniAGtP8hbt74wqL8Qvaw+wgB8e/7hZeobeS+gdkVf1uAkuPalHJlp46XKRTA5ZqyE='
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///labs.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(300), nullable=False)
    user_surname = db.Column(db.String(300), nullable=False)
    user_email = db.Column(db.String(2025), nullable=False)
    user_password = db.Column(db.String, nullable=False)
    user_old = db.Column(db.Integer, nullable=False)
    user_work = db.Column(db.String(300))
    user_img = db.Column(db.String(2025))

    def __repr__(self):
        return f'<user {self.user_id}> '

    def get_id(self):
        return self.user_id


class News(db.Model):
    __tablename__ = "news"
    news_id = db.Column(db.Integer, primary_key=True)
    news_title = db.Column(db.String(144), nullable=True)
    news_intro = db.Column(db.String(300), nullable=True)
    news_text = db.Column(db.Text, nullable=True)
    news_date = db.Column(db.DateTime, default=dt.utcnow())

    def __repr__(self):
        return f'<news {self.news_id}>'


class User_info:
    id = 3
    name = "admin"
    surname = "admin"
    login = "admin@admin.ru"
    password = "root"
    old = "0"
    work = "admin"


@app.route('/')
@app.route('/home')
def index():
    l = len(os.listdir('static/download'))
    j = len(os.listdir('data/json'))
    img_path = f"../static/download/picture_{l - 1}.jpg"
    federal_area = ""
    city = ""
    with open(f'data/json/result_{j - 1}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        country = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['description']
        federal_area = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData']['AddressDetails']['Country']["AdministrativeArea"]["AdministrativeAreaName"]
        city = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
    return render_template('index.html', img=img_path, country=country, federal_area=federal_area, city=city)


@app.route('/city-map/<string:city>')
def city_map(city):
    data = yap.get_pos(city)
    longitude = data['longitude']
    width = data['width']
    data = data['data']
    country = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['description']
    federal_area = \
        data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData'][
            'AddressDetails']['Country']["AdministrativeArea"]["AdministrativeAreaName"]
    city = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
    img_name = yap.get_map(longitude, width)['img_name']
    img_path = f'../static/download/{img_name}'
    return render_template('search.html', img=img_path, country=country, federal_area=federal_area, city=city)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


@app.route('/admin/', methods=['get', 'post'])
@login_required
def admin():
    if current_user.user_email != "admin@admin.ru" and current_user.user_password != "admin":
        return redirect(url_for('registration'))
    user_id = request.args.get('user_id')
    form = ChangeUserForm()
    message = ""
    try:
        user_response = db.session.query(User).filter(User.user_id == user_id).one()
    except Exception as e:
        print(e)
    else:
        user_info = User_info()
        user_info.id = user_response.user_id
        user_info.name = user_response.user_name
        user_info.surname = user_response.user_surname
        user_info.login = user_response.user_email
        user_info.old = user_response.user_old
        user_info.work = user_response.user_work

    if request.method == 'POST':
        data = dict({
            'name': user_info.name,
            'surname': user_info.surname,
            'login': user_info.login,
            'old': user_info.old,
            'work': user_info.work
        })
        new_data = dict({
            'name': form.name.data,
            'surname': form.surname.data,
            'login': form.email.data,
            'old': form.old.data,
            'work': form.work.data
        })
        if new_data['name'] and new_data['name'] != data['name']:
            data['name'] = new_data['name']
        if new_data['surname'] and new_data['surname'] != data['surname']:
            data['surname'] = new_data['surname']
        if new_data['login'] and new_data['login'] != data['login']:
            data['login'] = new_data['login']
        if new_data['old'] and new_data['old'] != data['old']:
            data['old'] = new_data['old']
        if new_data['work'] and new_data['work'] != data['work']:
            data['work'] = new_data['work']

        try:
            update_query = db.session.query(User).filter(User.user_id == user_id).update({User.user_name: data['name'], User.user_surname: data['surname']}, synchronize_session=False)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            message = "Изменение данных в бд прошло с ошибкой!"
            print(e)
        else:
            return redirect(url_for('admin', user_id=user_id))

    return render_template('admin.html', form=form, message=message, data=user_info)


@app.route('/admin-choice/', methods=['get', 'post'])
def admin_choice():
    if current_user.user_email != "admin@admin.ru" and current_user.user_password != "admin":
        return redirect(url_for('registration'))
    select_form = SelectUserForm()
    list_data = list()
    user_id = 3
    users = db.session.query(User).order_by(User.user_id).all()
    for i in range(len(users)):
        list_data.append((str(users[i].user_id), users[i].user_email))
    select_form.id.default = ['3']
    select_form.id.choices = list_data
    if request.method == "POST":
        print(int(select_form.id.data[0]))
        user_id = int(select_form.id.data[0])
        return redirect(url_for('admin', user_id=user_id))
    return render_template('admin_choice_form.html', select_form=select_form)


@app.route('/profile/', methods=['get', 'post'])
@login_required
def profile():
    if not current_user.is_authenticated:
        return redirect('login')
    form = ChangeUserForm()
    message = ""
    if request.method == 'POST':
        data = dict({
            'name': current_user.user_name,
            'surname': current_user.user_surname,
            'login': current_user.user_email,
            'password': current_user.user_password,
            'old': current_user.user_old,
            'work': current_user.user_work
        })

        new_data = dict({
            'name': form.name.data,
            'surname': form.surname.data,
            'login': form.email.data,
            'password': form.password.data,
            'confirm_password': form.confirm_password.data,
            'old': form.old.data,
            'work': form.work.data
        })
        user = db.session.query(User).filter_by(user_id=current_user.user_id).one()
        if new_data['name'] and new_data['name'] != data['name']:
            data['name'] = new_data['name']
        if new_data['surname'] and new_data['surname'] != data['surname']:
            data['surname'] = new_data['name']
        if new_data['login'] and new_data['login'] != data['login']:
            data['login'] = new_data['login']
        if new_data['old'] and new_data['old'] != data['old']:
            data['old'] = new_data['old']
        if new_data['work'] and new_data['work'] != data['work']:
            data['work'] = new_data['work']
        if not check_password(data['password'], new_data['password']) and new_data['password'] == new_data['confirm_password']:
            data['password'] = hash_password(new_data['password'])

        user.user_name = data['name']
        user.user_surname = data['surname']
        user.user_email = data['login']
        user.user_password = data['password']
        user.user_old = data['old']
        user.user_work = data['work']

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            message = "Изменение данных в бд прошло с ошибкой!"
            print(e)
        else:
            current_user.user_name = data['name']
            current_user.user_surname = data['surname']
            current_user.user_email = data['login']
            current_user.user_password = data['password']
            current_user.user_old = data['old']
            current_user.user_work = data['work']
            return redirect('/profile/')

    return render_template('profile.html', form=form, message=message)


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    message = ""
    if request.method == 'POST':
        login = form.email.data
        user = db.session.query(User).filter(User.user_email == login).first()
        if check_password(user.user_password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('auth_form.html', form=form, message=message)


def does_user_exist(email):
    user = db.session.query(User).filter(User.user_email == email).first()
    if user is None:
        return None
    else:
        return "Такой пользователь уже существует!"


@app.route('/reg', methods=['post', 'get'])
def registration():
    form = CreateUserForm()
    message = ""
    if form.validate_on_submit():
        data = dict({
            'name': form.name.data,
            'surname': form.surname.data,
            'email': form.email.data,
            'password': hash_password(form.password.data),
            'old': form.old.data,
            'work': form.work.data
                    })
        try:
            find_person = does_user_exist(data['email'])
            if find_person is None:
                new_user = User(user_name=data['name'], user_surname=data['surname'], user_email=data['email'], user_password=data['password'], user_old=data['old'], user_work=data['work'], user_img='000.jpg')
                db.session.add(new_user)
                db.session.commit()
            else:
                message = find_person
                raise Exception(message)
        except Exception as e:
            print(e)
        else:
            return redirect(url_for('login'))
    return render_template('reg_form.html', form=form, message=message)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
