import os, json

from flask import Flask, render_template, url_for, request
import hashlib, uuid
from flask_sqlalchemy import SQLAlchemy
from yapi import YaAPI as yap
from datetime import datetime as dt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///labs.sqlite"
db = SQLAlchemy(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(300), nullable=False)
    user_surname = db.Column(db.String(300), nullable=False)
    user_email = db.Column(db.String(2025), nullable=False)
    user_password = db.Column(db.String, nullable=False)
    user_workname = db.Column(db.String(300))
    user_img = db.Column(db.String(2025))

    def __repr__(self):
        return f'<user {self.user_id}> '


class News(db.Model):
    __tablename__ = "news"
    news_id = db.Column(db.Integer, primary_key=True)
    news_title = db.Column(db.String(144), nullable=True)
    news_intro = db.Column(db.String(300), nullable=True)
    news_text = db.Column(db.Text, nullable=True)
    news_date = db.Column(db.DateTime, default=dt.utcnow())

    def __repr__(self):
        return f'<news {self.news_id}>'


@app.route('/')
def index():
    l = len(os.listdir('static/download'))
    j = len(os.listdir('data/json'))
    img_path = f"../static/download/picture_{l - 1}.jpg"
    federal_area = ""
    city = ""
    with open(f'data/json/result_{j - 1}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        country = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['description']
        federal_area = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']["AdministrativeArea"]["AdministrativeAreaName"]
        city = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
    return render_template('index.html', img=img_path, country=country, federal_area=federal_area, city=city)


@app.route('/city-map/<string:city>')
def city_map(city):
    data = yap.get_pos(city)
    longitude = data['longitude']
    width = data['width']
    data = data['data']
    country = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['description']
    federal_area = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']["AdministrativeArea"]["AdministrativeAreaName"]
    city = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
    img_name = yap.get_map(longitude, width)['img_name']
    img_path = f'../static/download/{img_name}'
    return render_template('search.html', img=img_path, country=country, federal_area=federal_area, city=city)


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


def from_validate():
    pass


@app.route('/auth',  methods=['post', 'get'])
def auth():
    user_email = ""
    user_password = ""
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = hash_password(request.form.get('password'))
    print(user_email)
    print(user_password)
    if user_email == 'admin@admin.ru' and user_password == 'admin':
        message = 'Correct username and password'
    else:
        message = 'Wrong username or password'

    return render_template('auth_form.html', message=message)

#
# @app.route('/reg', method=['post', 'get'])
# def registration():
#     # user_name = ""
#     # user_surname = ""
#     # user_email = ""
#     # user_password = ""
#     # if request.method == 'POST':
#     #     user_name = request.form.get('username')
#     #     user_surname = request.form.get('surname')
#     #     user_email = request.form.get('email')
#     #     user_password = request.form.get('password')
#     #     user_workname = request.form.get('workname')
#     #     user_img = request.form.get('img')
#     # print(user_name)
#     # # if not user_name or not user_surname or not user_email or not user_password or not user_workname:
#     # #     message = 'Заполните все поля!'
#
#     return render_template('reg_form.html')


if __name__ == "__main__":
    app.run(debug=True)
