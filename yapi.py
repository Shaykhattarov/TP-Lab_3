import json
import os
import requests as req


class YaAPI:

    @staticmethod
    def get_pos(city):
        token = 'abf6ba70-553c-4715-b061-ffe5618e5702'
        url_geo = f'https://geocode-maps.yandex.ru/1.x/'
        if not city:
            city = 'Ульяновск'
        url = url_geo + f'?apikey={token}&geocode={city}&format=json'
        try:
            response = req.get(url)
            if response.status_code != 200:
                raise Exception(response.status_code)
        except Exception as err:
            return dict(code=err)
        else:
            dir = os.listdir('data/json/')
            with open(f'data/json/result_{len(dir)}.json', 'w', encoding='utf-8') as file:
                file.write(response.text)
            dict_res = json.loads(response.content)
            position = dict_res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
            longitude = position[0]
            width = position[1]
            return dict(code=response.status_code, data=dict_res, longitude=longitude, width=width)

    @staticmethod
    def get_map(longitude, width):
        token = 'abf6ba70-553c-4715-b061-ffe5618e5702'
        url_static = f'http://static-maps.yandex.ru/1.x/'
        if not longitude or not width:
            longitude = 48.384824
            width = 54.151718
        spn = [0.3, 0.3]
        size_w = 450
        size_h = 450
        scheme_l = 'map'
        url = url_static + f'?apikey={token}&ll={longitude},{width}&' \
                                  f'spn={spn[0]},{spn[1]}&size={size_w},{size_h}&l={scheme_l}'
        try:
            response = req.get(url)
            if response.status_code != 200:
                raise Exception(response.status_code)
        except Exception as err:
            return dict(code=err, longitude=longitude, width=width)
        else:
            dir = os.listdir('static/download/')
            with open(f'static/download/picture_{len(dir)}.jpg', 'wb') as file:
                file.write(response.content)
            return dict(code=response.status_code, img_name=f'picture_{len(dir)}.jpg')


