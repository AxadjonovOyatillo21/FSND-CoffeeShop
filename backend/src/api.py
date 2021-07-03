import os
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError
import json
from . import app
from .database.models import Drink
from .auth.auth import AuthError, requires_auth


@app.route('/drinks')
def get_all_drinks():
    query_drinks = Drink.query.all()
    drinks = [drink.short() for drink in query_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_all_drinks_detail(payload):
    query_drinks = Drink.query.all()
    drinks = [drink.long() for drink in query_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def add_new_drink(payload):
    data = request.get_json() or abort(400)
    title = data['title'] or abort(400)
    recipe = data['recipe'] or abort(400)
    recipe = json.dumps(recipe)
    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
    except SQLAlchemyError:
        abort(422)
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(payload, drink_id: int):
    data = request.get_json() or abort(400)
    drink = Drink.query.get_or_404(drink_id)
    if "title" in data:
        drink.title = data['title']
    if "recipe" in data:
        drink.recipe = json.dumps(data['recipe'])
    try:
        drink.update()
    except SQLAlchemyError:
        abort(422)
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(payload, drink_id: int):
    drink = Drink.query.get_or_404(drink_id)
    try:
        drink.delete()
    except SQLAlchemyError:
        abort(422)
    return jsonify({
        "success": True,
        "delete": drink_id
    })


# Error Handlers


@app.errorhandler(400)
def bad_request(e):
    return jsonify({
        "success": False,
        "code": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(e):
    return jsonify({
        "success": False,
        "code": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def unauthorized(e):
    return jsonify({
        "success": False,
        "code": 403,
        "message": "forbidden: access denied"
    }), 403


@app.errorhandler(422)
def unprocessable_entity(e):
    return jsonify({
        "success": False,
        "code": 422,
        "message": "unprocessable entity"
    }), 422


@app.errorhandler(500)
def unprocessable_entity(e):
    return jsonify({
        "success": False,
        "code": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def authentication_error(e: AuthError):
    return jsonify({
        "success": False,
        "code": e.status_code,
        "message": e.error
    }), e.status_code