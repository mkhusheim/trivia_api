import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Helper method for paginating questions


def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in questions]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    db = SQLAlchemy(app)
    '''
  CORS setup. Allows '*' for origins.
  '''
    CORS(app)
    '''
  After_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
  Endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type
        return jsonify({"categories": formatted_categories})

    '''
  Endpoint to handle GET requests for questions,
  pagination (every 10 questions).
  '''
    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by('id').all()
        current_questions = paginate_questions(request, questions)
        if len(current_questions) == 0:
            abort(404)
        categories = db.session.query(Category, Question).filter(Category.id == Question.category)
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.Category.id] = category.Category.type
        return jsonify(
            {
                "questions": current_questions,
                "totalQuestions": len(questions),
                "categories": formatted_categories
            })

    '''
  Endpoint to DELETE question using a question ID.
  '''
    @app.route('/questions/<int:question_id>', methods=['GET', 'DELETE'])
    def delete_question(question_id):
        try:
            selected_question = Question.query.filter(Question.id == question_id).one_or_none()
            if selected_question is None:
                abort(404)
            selected_question.delete()
            questions = Question.query.order_by('id').all()
            current_questions = paginate_questions(request, questions)
        except:
            abort(422)
        return jsonify(
            {
                "questions": current_questions,
            })

    '''
  Endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.
  '''
    @app.route('/questions', methods=['GET', 'POST'])
    def new_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty_score = body.get('difficulty')
        try:
            new_question = Question(question=question, answer=answer,
                                    category=category, difficulty=difficulty_score)
            new_question.insert()
            questions = Question.query.order_by('id').all()
            current_questions = paginate_questions(request, questions)
            return jsonify(
                {
                    "questions": current_questions,
                    "totalQuestions": len(questions),
                    "currentCategory": category
                })
        except:
            abort(422)

    '''
  POST endpoint to get questions based on a search term.
  '''
    @app.route('/questions/search', methods=['GET', 'POST'])
    def search_question():
        body = request.get_json()
        search_value = body.get('searchTerm', None)
        search_format = "%{}%".format(search_value)
        print(search_format)
        try:
            search_result = Question.query.filter(Question.question.ilike(search_format)).all()
            print(search_result)
            if len(search_result) == 0:
                abort(404)
            categories = Category.query.all()
            formatted_categories = {}
            for category in categories:
                formatted_categories[category.id] = category.type
            return jsonify({
                "questions": [question.format() for question in search_result],
                "totalQuestions": len(search_result),
                "currentCategory": formatted_categories
            })
        except:
            abort(422)

    '''
  GET endpoint to get questions based on category.
  '''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).all()
        current_questions = paginate_questions(request, questions)
        if len(current_questions) == 0:
            abort(404)
        return jsonify(
            {
                "questions": current_questions,
                "totalQuestions": len(questions),
                "currentCategory": category_id
            })

    '''
  POST endpoint to get questions to play the quiz.
  This endpoint takes category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.
  '''
    @app.route('/quizzes', methods=['GET', 'POST'])
    def play_quiz():
        body = request.get_json()
        quiz_category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)
        try:
            if quiz_category['id'] != 0:
                questions = Question.query.filter(Question.category == quiz_category['id']).all()
            else:
                questions = Question.query.all()
            current_questions = paginate_questions(request, questions)
            for question in current_questions:
                if question in previous_questions:
                    question.pop()
            random_question = random.choice(current_questions)
            print(random_question)
            previous_questions.append(random_question)
            print(previous_questions)
            return jsonify({
                "question": random_question
            })
        except:
            abort(422)

    '''
  error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    return app
