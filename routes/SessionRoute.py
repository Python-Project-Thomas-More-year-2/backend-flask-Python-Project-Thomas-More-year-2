import random

from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource
from werkzeug.exceptions import Unauthorized

from models import db, Session, User

schema_post = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 15,
                    "pattern": "^[a-zA-Z0-9 \\-_+]+$",
                }
            },
            "required": ["name"],
        },
    },
    "required": ["user"],
}

schema_patch = {
    "type": "object",
    "properties": {
        "session": {
            "type": "object",
            "properties": {
                "startCapital": {
                    "type": "integer",
                    "minimum": 0,
                },
                "seeOthersBalance": {
                    "type": "boolean",
                },
                "goReward": {
                    "type": "integer",
                    "minimum": 0,
                },
                "freeParking": {
                    "type": "boolean",
                },
            },
            "required": [
                "startCapital",
                "seeOthersBalance",
                "goReward",
                "freeParking",
            ],
        },
    },
    "required": ["session"],
}


def generate_random_string(n=3):
    return ''.join(chr(random.randint(65, 90)) for _ in range(n))


def generate_session_code():
    return f"{generate_random_string()}-{generate_random_string()}"


class SessionRoute(Resource):
    @staticmethod
    def get():
        if session.get("user_id") is None:
            raise Unauthorized("User has no connected session")

        user: User = User.query.filter_by(id=session["user_id"]).first()

        return {
                   "session": {
                       "id": user.session.id,
                       "code": user.session.code,
                       "startCapital": user.session.startCapital,
                       "seeOthersBalance": user.session.seeOthersBalance,
                       "goReward": user.session.goReward,
                       "freeParkingMoney": user.session.freeParkingMoney,
                       "freeParking": user.session.freeParking,
                   }
               }, 200

    @staticmethod
    @expects_json(schema_post)
    def post():
        # Get JSON-data body from request
        req = request.get_json()

        # Generate connection code and check if a session already exists with this code,
        # try again if there is a duplicate.
        code = generate_session_code()
        duplicate = Session.query.filter_by(code=code).first()
        while duplicate is not None:
            code = generate_session_code()
            duplicate = Session.query.filter_by(code=code).first()

        # Create monopoly-session object
        ses = Session(
            code=code,
            startCapital=1500,
            seeOthersBalance=True,
            goReward=200,
            freeParkingMoney=0,
            freeParking=True,
        )

        # Store this monopoly-session-object
        db.session.add(ses)
        db.session.commit()

        # Create monopoly-user object
        user = User(
            session_id=ses.id,
            money=0,
            name=req["user"]["name"],
            isHost=True,
            isBank=True,
        )

        # Store this user
        db.session.add(user)
        db.session.commit()

        # Store user-id in flask-session
        session["user_id"] = user.id

        # Respond
        return {
                   "session": {
                       "id": ses.id,
                       "code": ses.code,
                       "startCapital": ses.startCapital,
                       "seeOthersBalance": ses.seeOthersBalance,
                       "goReward": ses.goReward,
                       "freeParkingMoney": ses.freeParkingMoney,
                       "freeParking": ses.freeParking
                   },
                   "user": {
                       "id": user.id,
                       "session_id": user.session_id,
                       "money": user.money,
                       "name": user.name,
                       "isHost": user.isHost,
                       "isBank": user.isBank
                   }
               }, 201

    @staticmethod
    @expects_json(schema_patch)
    def patch():
        if session.get("user_id") is None:
            raise Unauthorized("User does not exist")

        user: User = User.query.filter_by(id=session["user_id"]).first()

        if not user.isHost:
            raise Unauthorized("You are not the host")

        req = request.get_json()

        user.session.startCapital = req["session"]["startCapital"]
        user.session.seeOthersBalance = req["session"]["seeOthersBalance"]
        user.session.goReward = req["session"]["goReward"]
        user.session.freeParking = req["session"]["freeParking"]

        db.session.commit()

        ses: Session = user.session

        return {
                   "session": {
                       "id": ses.id,
                       "code": ses.code,
                       "startCapital": ses.startCapital,
                       "seeOthersBalance": ses.seeOthersBalance,
                       "goReward": ses.goReward,
                       "freeParkingMoney": ses.freeParkingMoney,
                       "freeParking": ses.freeParking,
                   }
               }, 200
