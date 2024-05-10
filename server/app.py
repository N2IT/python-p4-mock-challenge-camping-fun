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

    def post(self):
        form_data = request.get_json() # check if this is deprecated and what to use instead
        name = form_data.get('name')
        age = form_data.get('age')
        if name == "":
            return {"errors" : "A name must be entered."}, 400
        if not 8 <= age <= 18:
            return {'errors' : 'Age must be between 8 and 18.'}, 400
        if form_data:            
            try:
                new_camper = Camper(
                    name = name,
                    age = age
                )
                db.session.add(new_camper)
                db.session.commit()
                return make_response(
                    new_camper.to_dict(),
                    201
                )
            except ValueError:
                return {'errors' : 'Validation errors'}, 400


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

    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        form_data = request.get_json()
        if form_data.get('name') == "":
            return {"errors" : ['validation errors']}, 400
        if not 8 <= form_data.get('age') <= 18:
            return {'errors' : ['validation errors']}, 400
        if camper:
            for attr in form_data:
                setattr(camper, attr, form_data.get(attr))
            db.session.commit()
            return make_response(
                camper.to_dict(rules = ('-signups',)),
                202
            )
        else:
            return {"error" : '404: Camper not found'}, 404     


class Activites(Resource):
    def get(self):
        activity = [activity.to_dict() for activity in Activity.query.all()]
        if activity:
            return make_response(
                activity,
                200
            )

        
class ActivitiesById(Resource):
    def get(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if activity:
            return make_response(
                activity.to_dict(),
                200
            )
        else:
            return {'error' : 'Activity not found'}, 404

    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return {}, 204

        else:
            return {'error' : 'Activity not found'}, 404


class Signups(Resource):
    def get(self):
        signup = [signup.to_dict() for signup in Signup.query.all()]
        if signup:
            return make_response(
                signup,
                200
            )

    def post(self):
        form_data = request.get_json()
        
        if form_data:
            if not 0 < form_data.get('time') < 23:
                return {'errors' : ['validation errors']}, 400

            

            new_signup = Signup(
                time = form_data.get('time'),
                camper_id = form_data.get('camper_id'),
                activity_id = form_data.get('activity_id')
            )

            db.session.add(new_signup)
            db.session.commit()

            return make_response(
                new_signup.to_dict(),
                201
            )
        
        else:
            return {'errors' : 'No form data entered'}, 400



api.add_resource(Campers, '/campers')
api.add_resource(CampersById, '/campers/<int:id>')
api.add_resource(Activites, '/activities')
api.add_resource(ActivitiesById, '/activities/<int:id>')
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=8888, debug=True)
