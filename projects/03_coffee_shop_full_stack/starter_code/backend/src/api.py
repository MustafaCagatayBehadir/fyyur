import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    _error_code = None
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        if len(drinks) == 0:
            _error_code = 404
            abort(404)
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        })
    except:
        print(sys.exc_info())
        _error_code = 422 if _error_code is None else _error_code
        abort(_error_code)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(payload):
    _error_code = None
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        if len(drinks) == 0:
            _error_code = 404
            abort(404)
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200
    except:
        print(sys.exc_info())
        _error_code = 422 if _error_code is None else _error_code
        abort(_error_code)    


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drinks(payload):
    try:
        body = request.get_json()
        drink = Drink(title=body['title'], recipe=json.dumps(body['recipe']))
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drinks(payload, id):
    _error_code = None
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            _error_code = 404
            abort(404)
        drink.title = body['title']
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        print(sys.exc_info())
        _error_code = 422 if _error_code is None else _error_code
        abort(_error_code)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drinks(payload, id):
    _error_code = None
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            _error_code = 404
            abort(404)
        drink.delete()
        return jsonify({
            "success": True,
            "drinks": id
        }), 200
    except:
        print(sys.exc_info())
        _error_code = 422 if _error_code is None else _error_code
        abort(_error_code)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_failed(autherror):
    return jsonify({
        "success": False,
        "error": autherror.status_code,
        "message": autherror.error["description"]
    }), autherror.status_code
    


if __name__ == "__main__":
    app.debug = True
    app.run()
