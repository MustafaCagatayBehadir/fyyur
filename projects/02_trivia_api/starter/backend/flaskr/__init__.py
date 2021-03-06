from crypt import methods
import sys
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():
        _error_code = None
        try:
            categories = Category.query.order_by(Category.id).all()

            if len(categories) == 0:
                _error_code = 404
                abort(404)

            return jsonify({
                'categories': {category.id: category.type for category in categories}
            })
        except:
            print(sys.exc_info())
            _error_code = 422 if _error_code is None else _error_code
            abort(_error_code)

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

    @app.route('/questions')
    def get_questions():
        _error_code = None
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            categories = Category.query.order_by(Category.id).all()

            if len(current_questions) == 0 or len(categories) == 0:
                _error_code = 404
                abort(404)

            return jsonify({
                'questions': current_questions,
                'total_questions': len(selection),
                'categories': {category.id: category.type for category in categories},
                'current_category': None
            })
        except:
            print(sys.exc_info())
            _error_code = 422 if _error_code is None else _error_code
            abort(_error_code)

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        _error_code = None
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                _error_code = 404
                abort(404)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id,
                'total_questions': len(Question.query.all()),
                'questions': [question.format() for question in Question.query.order_by(Question.id).all()]
            })
        except:
            db.session.rollback()
            print(sys.exc_info())
            _error_code = 422 if _error_code is None else _error_code
            abort(_error_code)
        finally:
            db.session.close()

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def add_search_question():
        body = request.get_json()
        if body.get('searchTerm') is None:
            return add_question(body)
        else:
            return search_question(body)

    def add_question(body):
        try:
            question = Question(
                body['question'], body['answer'], body['category'], body['difficulty'])
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except Exception as e:
            print(e)
            db.session.rollback()
            print(sys.exc_info())
            abort(422)
        finally:
            db.session.close()

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    def search_question(body):
        try:
            search_term = body['searchTerm']
            return jsonify({
                'questions': [question.format() for question in Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()],
                'total_questions': len(Question.query.all()),
                'current_category': None
            })
        except:
            abort(422)

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        _error_code = None
        try:
            questions = Question.query.filter(
                Question.category == category_id).order_by(Question.id).all()
            if len(questions) == 0:
                _error_code = 404
                abort(404)

            return jsonify({
                'questions': [question.format() for question in questions],
                'total_questions': len(Question.query.filter(Question.category == category_id).all()),
                'current_category': Category.query.filter(Category.id == category_id).one_or_none().type
            })
        except:
            print(sys.exc_info())
            _error_code = 422 if _error_code is None else _error_code
            abort(_error_code)

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def play_trivia():
        _error_code = None
        try:
            body = request.get_json()
            if int(body['quiz_category']['id']) != 0:
                questions = Question.query.filter(Question.category == int(
                    body['quiz_category']['id'])).order_by(Question.id).all()
            else:
                questions = Question.query.order_by(Question.id).all()

            if len(questions) == 0:
                _error_code = 404
                abort(404)

            formatted_questions = [question.format() for question in questions]
            while len(formatted_questions) != len(body['previous_questions']):
                question = random.choice(formatted_questions)
                if question['id'] not in body['previous_questions']:
                    break
            else:
                question = None
            return jsonify({
                'question': question
            })
        except:
            print(sys.exc_info())
            _error_code = 422 if _error_code is None else _error_code
            abort(_error_code)

    '''
  @TODO: 
  Create error handlers for all expected errors 
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

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    return app
