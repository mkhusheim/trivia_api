import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        self.new_question = ({
            "question": "Which team won gold and bronze medals in the Asian Archery Grand Prix held on March 12, 2013?",
            "answer": "India",
            "category": 6,
            "difficulty": 5
        })

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Test get questions
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])

    # Test delete question
    def test_delete_question(self):
        res = self.client().delete('/questions/24')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 24).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(question, None)

    # Test post a new question
    def test_post_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    # Test get questions by category
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        questions = Question.query.filter(Question.category == 1).all()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['currentCategory'])

    # Test get categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    # Test play quiz
    def test_play_quiz(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        questions = Question.query.filter(Question.category == 1).all
        previous_questions = [12, 12, 5]
        for question in questions:
            if question in previous_questions:
                question.pop()

        random_question = random.choice(questions)

        self.assertEqual(res.status_code, 200)
        self.asserTrue(data['question'])

    # Test not valid page number
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # Test question does not exist
    def test_422_question_does_not_exist(self):
        res = self.client().delete('/questions/2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # Test question post not allowed
    def test_405_question_post_not_allowed(self):
        res = self.client().post('/questions/40', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
