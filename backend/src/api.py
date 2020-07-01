import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import collections
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] =
    'Authorization, Content-Type, true'
    header['Access-Control-Allow-Methods'] =
    'POST,GET,PUT,DELETE,PATCH,OPTIONS'
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


@app.route("/drinks")
def get_drinks():
    # query all drinks in database
    drinks = Drink.query.all()
    drinks_list = {}
    drinks_list = collections.defaultdict(list)
    # fill the list with query result
    for drink in drinks:
        drinks_list[drink .id] = drink.short()

    return jsonify({
        "success": True,
        "drinks": drinks_list})


@app.route("/drink-details")
@requires_auth('get:drinks-detail')
def get_drinks_details(token):
    # query all drinks in database
    drinks = Drink.query.all()
    drinks_list = {}
    drinks_list = collections.defaultdict(list)
    # fill the list with drink details
    for drink in drinks:
        drinks_list[drink .id] = drink.long()

    return jsonify({
        "success": True,
        "drinks": drinks_list})


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    try:
        # get the request body
        Request_body = request.get_json()
        title = Request_body.get('title', None)
        recipe = Request_body.get('recipe', None)
        # create a drink object
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(token, drink_id):
    Request_body = request.get_json()
    # get the data to be modified
    title = Request_body.get('title', None)
    recipe = Request_body.get('recipe', None)
    # get the target drink to be modified
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if drink is None:
        abort(404)

    if title is not None:
        drink.title = title

    if recipe is not None:
        drink.recipe = json.dumps(recipe)

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token, drink_id):
    # get the drink to be deleted
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    # throw an error if drink does not exist
    if drink is None:
        abort(404)

    drink.delete()
    return jsonify({
        'success': True,
        'deleted': drink_id
    })


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"

    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
    }, 401)
