#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
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
api = Api(app)

@app.route('/')
def home():
    return ''


class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(rules = ('-signups',)) for camper in Camper.query.all()]
        if not campers:
            return {'errors' : '204: No content available'}, 204
        return make_response(
            campers,
            200
        )

class CampersById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            response = make_response(
                jsonify(camper.to_dict()),
                200
            )
        else:
            response = {'error' : 'Camper not found'}, 404

        return response

api.add_resource(Campers, '/campers')
api.add_resource(CampersById, '/campers/<int:id>')


if __name__ == '__main__':
    app.run(port=8888, debug=True)
