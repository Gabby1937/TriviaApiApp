import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from jinja2.utils import markupsafe
markupsafe.Markup()
from markupsafe import Markup


from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selections):
  page = request.args.get('page', 1, type=int)
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start+QUESTIONS_PER_PAGE 
  
  questions = [question.format() for question in selections]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app, resources={"/": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, PUT, POST, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        #for retrieving all the categories
        data = Category.query.all()
        categories = {}
        for category in data:
            categories[category.id] = category.type

        if len(data) == 0:
            abort(404)

        return jsonify({
        'success': True,
        'categories': categories
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        # for retrieving all questions and paginate
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # for retrieving all categories
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        # if no questions appears it aborts 404 
        if (len(current_questions) == 0):
            abort(404)

        # return to view data
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['GET','DELETE'])
    def delete_question(id):
        #delete the question with id

        try:
            question = Question.query.get(id)

            if question is None:
                abort(404)

            question.delete()
        
            return jsonify({
                'success': True,
                'deleted': id
            })
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():

        data = request.get_json()

        new_question = data['question']
        insert_answer = data['answer']
        insert_category = data['category']
        insert_difficulty = data['difficulty']

        if (len(new_question)==0) or (len(insert_answer)==0) or (len(insert_answer)==0) or (len(insert_answer)==0):
            abort(422)

        question = Question(
        question = new_question,
        answer = insert_answer,
        category = insert_category,
        difficulty = insert_difficulty,
        )

        question.insert()
    
        all_questions = Question.query.all()
        current_questions = paginate_questions(request, all_questions)

        return jsonify({
            'success': True,
            'created': question.id,
            'questions': current_questions,
            'total_questions': len(all_questions)
        })
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['GET','POST'])
    def search_questions():
        #searches for related questions with input string
        data = request.get_json()

        if(data['searchTerm']):
            search_term = data['searchTerm']

        related_questions = Question.query.filter(Question.question.like('%{}%'.format(search_term))).all()
        
        if related_questions==[]:
            abort(404)

        output = paginate_questions(request, related_questions)

        return jsonify({
        'success': True,
        'questions': output,
        'total_questions': len(related_questions)
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_question_by_category(id):
        category = Category.query.get(id)
        if (category is None):
            abort(404)

        try:
            questions = Question.query.filter_by(category=category.id).all()
        
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'current_category': category.type,
                'total_questions': len(questions)
            })
        except:
            abort(500)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_a_quiz_question():
        '''
        Input: category id and ids of previous questions'
        Output: a random question
        '''
        data = request.get_json()

        category = data['quiz_category']
        previous_questions = data['previous_questions']

        #for selection of a category
        if category['id'] != 0:
            questions = Question.query.filter_by(category=category['id']).all()
        #for selection of "All"
        else:
            questions = Question.query.all()

        def get_random_question():
            next_question = random.choice(questions).format()
            return next_question

        next_question = get_random_question()

        used = False
        if next_question['id'] in previous_questions:
            used = True

        while used:
            next_question = random.choice(questions).format()

        if (len(previous_questions) == len(questions)):
            return jsonify({
            'success': True,
            'message': "game over"
            }), 200

        return jsonify({
        'success': True,
        'question': next_question
        })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found. Input out of range.'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        'success': False,
        'error': 422, 
        'message': 'unprocessable. Synax error.'
        }), 422

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
        'success': False,
        'error': 500, 
        'message': 'Sorry, the falut is us not you. Please try again later.'
        }), 500


    return app

