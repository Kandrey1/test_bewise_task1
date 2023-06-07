import asyncio
import aiohttp

from .models import Questions, db


async def add_new_questions_in_db(questions: dict) -> int:
    """
    Добавляет в БД вопросы.
    Получает словарь с вопросами. Создает список id вопросами,
    которые уже есть в БД. Добавляет вопросы в БД если их нет в этом списке.
    Возвращает количество записей добавленных в БД.

    :param questions: Словарь с вопросами, которые необходимо добавить в БД.

    """
    lst_id_questions = [v.get('id') for k, v in questions.items()]

    repeated_questions = Questions.query.filter(
        Questions.question_id.in_(lst_id_questions)).all()

    repeated_id = {question.question_id for question in repeated_questions}

    for k, v in questions.items():
        if v.get('id') not in repeated_id:
            new = Questions(question_id=v.get('id'),
                            create=v.get('created_at'),
                            question_text=v.get('question'),
                            answer=v.get('answer'),
                            name_category=v.get('category').get(
                                'title'))
            db.session.add(new)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return 0

    return len(lst_id_questions) - len(repeated_id)


async def get_last_question() -> [dict, list]:
    """
    Возвращает последний добавленный в БД вопрос.
    """
    last_row = []
    row = Questions.query.order_by(Questions.id.desc()).first()
    if row:
        last_row = {'id_database': row.id,
                    'category': row.name_category,
                    'ID': row.question_id,
                    'question': row.question_text,
                    'answer': row.answer,
                    'date_create': row.create}
    return last_row


async def get_lst_tasks(session: aiohttp.ClientSession, need_cnt: int) -> list:
    """
    Создает список задач(запросов к стороннему сайту.)

    :param session: Сессия запроса.
    :param need_cnt: Число вопросов, которые необходимо добавит.
    """
    tasks = []
    n = need_cnt // 100
    k = need_cnt % 100

    url = "https://jservice.io/api/random?count=100"
    for _ in range(n):
        task = asyncio.create_task(make_request(session=session,
                                                url=url))
        tasks.append(task)

    if k:
        url = f"https://jservice.io/api/random?count={k}"
        task = asyncio.create_task(make_request(session=session,
                                                url=url))
        tasks.append(task)

    return tasks


async def make_request(session: aiohttp.ClientSession, url: str):
    """
    Выполняет запрос(к стороннему сайту)
    Добавляет полученные данные в словарь.

    :param session: Сессия запроса.
    :param url: URL запроса
    """
    async with session.get(url) as resp:
        try:
            return await resp.json()

        except Exception:
            return None
