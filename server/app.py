#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists')
def get_scientists():
    all_scientists = Scientist.query.all()
    scientist_dictionary = [scientist.to_dict(rules=('-missions',)) for scientist in all_scientists]
    return make_response(jsonify(scientist_dictionary), 200)

@app.route('/scientists/<int:id>')
def get_scientist(id):
    scientist = db.session.get(Scientist, id)

    if scientist:
        return make_response(jsonify(scientist.to_dict()), 200)
    else:
        response_body = {
            "error": "Scientist not found"
        }
        return make_response(jsonify(response_body), 404)

@app.route('/scientists', methods=["POST"])
def add_scientist():
    name = request.json.get('name')
    field_of_study = request.json.get('field_of_study')
    try:
        new_scientist = Scientist(name=name, field_of_study=field_of_study)
        db.session.add(new_scientist)
        db.session.commit()
        response_body = new_scientist.to_dict()
        return make_response(jsonify(response_body), 201)
    except:
        response_body = {
            "errors": ["validation errors"]
        }
        return make_response(jsonify(response_body), 400)

@app.route('/scientists/<int:id>', methods=['PATCH'])
def update_scientist(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        response_body = {
            "error": "Scientist not found"
        }
        return make_response(jsonify(response_body), 404)
    else:
        try:
            for attr in request.json:
                setattr(scientist, attr, request.json.get(attr))
            db.session.commit()
            response_body = scientist.to_dict(rules=('-missions',))
            return make_response(jsonify(response_body), 202)
        except ValueError:
            response_body={
                "errors": ["validation errors"]
            }
            return make_response(jsonify(response_body), 400)

@app.route('/scientists/<int:id>', methods=['DELETE'])
def delete_scientist(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        response_body = {
            "error": "Scientist not found"
        }
        return make_response(jsonify(response_body), 404)
    else:
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)

@app.route('/planets')
def get_planets():
    all_planets = Planet.query.all()
    planet_dictionary = [planet.to_dict(rules=('-missions',)) for planet in all_planets]
    return make_response(jsonify(planet_dictionary), 200)


@app.route('/missions', methods = ['POST'])
def add_mission():
    name = request.json.get('name')
    scientist_id = request.json.get('scientist_id')
    planet_id = request.json.get('planet_id')
    try:
        new_mission = Mission(name=name, scientist_id=scientist_id, planet_id=planet_id)
        db.session.add(new_mission)
        db.session.commit()
        response_body = new_mission.to_dict()
        return make_response(jsonify(response_body), 201)
    except:
        response_body = {
            "errors": ["validation errors"]
        }
        return make_response(jsonify(response_body), 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)

