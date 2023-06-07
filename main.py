import asyncio
import aiohttp

from flask import jsonify, request

from app import create_app
from app.utils import get_last_question, get_lst_tasks, add_new_questions_in_db
from app.models import db

app = create_app()


@app.before_first_request
def create_table():
    db.create_all()


@app.route('/', methods=['GET'])
async def home():
    return jsonify({'page': 'home quiz'})


@app.route('/api/v1.0/quiz/', methods=['POST'])
async def quiz_questions():
    """Получение вопросов викторины."""
    try:
        count_need_questions = int(request.json.get('questions_num'))
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        async with aiohttp.ClientSession(connector=connector) as session:

            while count_need_questions > 0:
                dct_questions = dict()

                count_need = 500 if count_need_questions >= 500 else count_need_questions

                tasks = await get_lst_tasks(session=session,
                                            need_cnt=count_need)

                responses = await asyncio.gather(*tasks)

                cnt_bad_req = 0
                for response in responses:
                    if response:
                        for item in response:
                            dct_questions.update({int(item['id']): item})
                    else:
                        cnt_bad_req += 1

                if cnt_bad_req >= 5:
                    await asyncio.sleep(20)

                count_need_questions -= await add_new_questions_in_db(dct_questions)

    except Exception:
        return {'Error': 'An error occurred. Try again.'}

    return await get_last_question()


@app.errorhandler(405)
def method_not_allowed(e):
    """
    Метод для страницы запрещен.
    """
    return jsonify({'Error': f'Method <{request.method}> not allowed'}), 405


@app.errorhandler(404)
def page_not_found(e):
    """
    Страница не найдена.
    """
    return jsonify({'Error': 'Page NOT found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
