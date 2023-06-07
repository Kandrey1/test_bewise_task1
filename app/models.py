from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


ma = Marshmallow()
db = SQLAlchemy()


class Questions(db.Model):
    """Таблица вопросов викторины.
        question_id: ID вопроса присвоенной отдающим сайтом.
        create: Дата создания вопроса.
        question_text: Текст вопроса.
        answer: Ответ на вопрос.
        name_cat: Название категории вопроса.
    """
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, unique=True, nullable=False)
    create = db.Column(db.DateTime, nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    name_category = db.Column(db.String(150), nullable=False)

    def __init__(self, question_id, create, question_text, answer,
                 name_category):
        self.question_id = question_id
        self.create = create
        self.question_text = question_text
        self.answer = answer
        self.name_category = name_category

    def __repr__(self):
        return f"<{self.id} -" \
               f"category: {self.name_category}, " \
               f"ID:{self.question_id}, " \
               f"question: {self.question_text}, " \
               f"answer: {self.answer}>"


class QuestionsSchema(ma.Schema):
    class Meta:
        model = Questions
        fields = ('id', 'question_id', 'create', 'question_text', 'answer',
                  'name_category')
