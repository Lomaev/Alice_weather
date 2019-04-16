import requests

appid = "6a8d9e01be3b7c56f1b5eb58affba33f"


def get_weather(place, time=0):
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': place, 'type': 'like', 'units': 'metric', 'APPID': appid})
        data = res.json()

        city_id = data['list'][0]['id']

        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        t = data['main']['temp']
        t_word = 'тепло, ' if t > 15 else 'холодно, '
        return t_word + str(t) + '°C, ' + data['weather'][0]['description'] + '.'
    except Exception as e:
        print("Exception (find):", e)
        return 'погода недоступна. Ошибка ' + str(e)
