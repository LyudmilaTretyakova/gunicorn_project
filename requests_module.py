from flask import Flask, request, jsonify
import time
import marshmallow
import logs
import database as db
from database_validation import HhVacancyUserSchema, CianUserSchema


app = Flask(__name__)


def start_timer():
    request.start_time = time.time()


def stop_timer(response):
    total_time = (time.time() - request.start_time) * 1000
    logs.api_logger.info(f'{request.method}\t {request.path}\t - Total time: {total_time}')
    return response


def setup_metrics(application):
    application.before_request(start_timer)
    application.after_request(stop_timer)


def no_content(content):
    msg = 'no content'
    if not content:
        logs.api_logger.error('Request failed <400>:\t' + msg)
        return True
    else:
        return False


def log_decor(func):
    def wrapper(content):
        status, msg = func(content)
        logs.api_logger.info(f'{msg} <{status}>')
        return status
    return wrapper


@log_decor
def get_hh(content):
    db.get_vacancy()
    msg = "zaglushka GET hh"
    return 200, msg


@log_decor
def post_hh(content):
    try:
        data = HhVacancyUserSchema(strict=True).load(content).data
    except marshmallow.exceptions.ValidationError as e:
        return jsonify(e.messages), 400

    db.add_vacancy_user(data['company'], data['salary_min'], data['salary_max'],
                        data['currency'], data['station'], data['domain'])

    msg = "zaglushka POST hh"
    return 200, msg


@log_decor
def put_hh(content):
    db.update_domain(content.get('name_old'), content.get('name_now'))
    msg = "zaglushka PUT hh"
    return 200, msg


@log_decor
def del_hh(content):
    db.del_vacancy_user(content.get('id'))
    msg = "zaglushka DEL hh"
    return 200, msg


# @app.route('/')
# def index():
#    logs.api_logger.info('Test logging record <200>')
#    return "Hey, Alex!"


@app.route('/hh', methods=['GET', 'POST', 'PUT', 'DELETE'])
def hh_request():
    content = request.json
    if no_content(content):
        return '', 400

    if request.method == 'GET':
        return '', get_hh(content)

    if request.method == 'POST':
        return '', post_hh(content)

    if request.method == 'PUT':
        return '', put_hh(content)

    if request.method == 'DELETE':
        return '', del_hh(content)

    # ошибка в передаваемых данных(тип, кол-во ...)
    # msg = 'текст ошибки - ответ Marshmallow'
    # logs.api_logger.error('hh_db: record getting failed <400>\n' + msg)
    # return abort(400)

    # не найден ресурс(запись)
    # msg = 'текст ошибки - ответ бд/orm'
    # logs.api_logger.error('hh_db: record getting failed <404>\n' + msg)
    # return abort(404)

    # ошибка со стороны бд
    # msg = 'текст ошибки - ответ сервера'
    # logs.api_logger.error('hh_db: record getting failed <500>\n' + msg)
    # return abort(500)

    # return 200


@log_decor
def get_cian(content):
    db.get_flat()
    msg = "zaglushka Get cian"
    return 200, msg


@log_decor
def post_cian(content):
    try:
        data = CianUserSchema(strict=True).load(content).data
    except marshmallow.exceptions.ValidationError as e:
        return jsonify(e.messages), 400

    db.add_flat_user(data['count_rooms'], data['station'], data['price'],
                     data['floor'], data['square'], data['price_sq'], data['address'])

    msg = "zaglushka POST cian"
    return 200, msg


@log_decor
def put_cian(content):
    db.update_station(content.get('name_old'), content.get('name_now'))
    msg = "zaglushka PUT cian"
    return 200, msg


@log_decor
def del_cian(content):
    db.del_flat_user(content.get('id'))
    msg = "zaglushka DEL cian"
    return 200, msg


@app.route('/cian', methods=['GET', 'POST', 'PUT', 'DELETE'])
def cian_request():
    content = request.json
    if no_content(content):
        return '', 400

    if request.method == 'GET':
        return '', get_cian(content)

    if request.method == 'POST':
        return '', post_cian(content)

    if request.method == 'PUT':
        return '', put_cian(content)

    if request.method == 'DELETE':
        return '', del_cian(content)


if __name__ == '__main__':
    setup_metrics(app)
    app.run(host="127.0.0.1", port="5000")
