import requests
import datetime

appid = "6a8d9e01be3b7c56f1b5eb58affba33f"


def get_weather(place, time=0):
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': place, 'type': 'like', 'units': 'metric', 'APPID': appid})
        data = res.json()

        city_id = data['list'][0]['id']

        if time == 0:
            res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                               params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
            data = res.json()
            t = data['main']['temp']
            t_word = 'тепло, ' if t > 15 else 'холодно, '
            return t_word + str(t) + '°C, ' + data['weather'][0]['description'] + '.'
        else:
            res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                               params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
            data = res.json()
            date = datetime.date.today() + datetime.timedelta(time)

            for prediction in data['list']:
                if prediction['dt_txt'] == '%s 15:00:00' % (date):
                    clouds = 'облачно' if prediction['clouds']['all'] > 60 else 'малооблачно'
                    return prediction['weather'][0]['description'] + ', ' + clouds + ', температура ' + str(prediction['main']['temp']) + '°C.'
            return 'Error!'

    except Exception as e:
        print("Exception (find):", e)
        return 'погода недоступна. Ошибка ' + str(e)