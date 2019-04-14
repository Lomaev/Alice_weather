from flask import Flask, request
import logging
import json
from weather_module import get_weather

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

time_buttons = [
    {
        'title': 'Завтра.',
        'hide': True
    },
    {
        'title': 'Через три дня.',
        'hide': True
    },
    {
        'title': 'Через неделю.',
        'hide': True
    }
]

choice_buttons = [
    {
        'title': 'Спасибо, это всё.',
        'hide': True
    },
    {
        'title': 'Назови погоду на другую дату.',
        'hide': True
    },
    {
        'title': 'Назови погоду в другом месте.',
        'hide': True
    }
]


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Пожалуйста, назовите город, погоду в котором вы хотите узнать.'
        sessionStorage[user_id] = {
            'place': None,  # Тут будет храниться место.
            'time': 'now',  # Тут будет храниться время (через 3 дня, через неделю) и т. п.
            'waiting_for_time': False,
            'waiting_for_place': True
        }
        return

    if sessionStorage[user_id]['waiting_for_place']:
        city = get_place_from_responce(req)
        if city is None:
            res['response']['text'] = 'Не расслышала город. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['place'] = city
            sessionStorage[user_id]['waiting_for_place'] = False

            res['response']['text'] = f'Отлично, я знаю этот город. Сегодня в нём ' + get_weather(city)
            res['response']['buttons'] = choice_buttons
            return
    elif sessionStorage[user_id]['waiting_for_time']:
        correct_requests = {'Завтра.': 1,
                            'Через три дня.': 3,
                            'Через неделю.': 7}  # Возможные варианты запросов - те, которые предлагались в диалоге.
        if req['request']['original_utterance'] in correct_requests:
            sessionStorage[user_id]['waiting_for_time'] = False

            if correct_requests[req['request']['original_utterance']] == 1:
                res['response']['text'] = f'Завтра в городе ' + sessionStorage[user_id]['place'] + get_weather(
                    sessionStorage[user_id]['place'], time=1)
            elif correct_requests[req['request']['original_utterance']] == 3:
                res['response']['text'] = f'Через 3 дня в городе ' + sessionStorage[user_id]['place'] + get_weather(
                    sessionStorage[user_id]['place'], time=3)
            else:
                res['response']['text'] = f'Через 7 дней в городе ' + sessionStorage[user_id]['place'] + get_weather(
                    sessionStorage[user_id]['place'], time=7)
            res['response']['buttons'] = choice_buttons
        else:
            res['response']['text'] = f'Некорректный запрос.'
            res['response']['buttons'] = time_buttons
    else:
        if req['request']['original_utterance'] == 'Спасибо, это всё.':
            res['response']['text'] = 'Приятно было работать с вами!'
            res['response']['end_session'] = True
        elif req['request']['original_utterance'] == 'Назови погоду на другую дату.':
            res['response']['text'] = 'Тогда скажите, погоду через сколько дней вам назвать.'
            sessionStorage[user_id]['waiting_for_time'] = True
            res['response']['buttons'] = time_buttons
        elif req['request']['original_utterance'] == 'Назови погоду в другом месте.':
            res['response']['text'] = 'Тогда скажите, погоду где вам назвать.'
            sessionStorage[user_id]['waiting_for_place'] = True


def get_place_from_responce(req):  # Вытаскиваем название города из запроса.
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


if __name__ == '__main__':
    app.run()
