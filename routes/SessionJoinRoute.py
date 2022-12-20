from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource
from werkzeug.exceptions import NotFound, Conflict

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
        "session": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "pattern": "^[a-zA-Z]{3}-[a-zA-Z]{3}$",
                }
            },
            "required": ["code"],
        },
    },
    "required": ["user", "session"],
}


class SessionJoinRoute(Resource):
    @staticmethod
    @expects_json(schema_post)
    def post():
        req = request.get_json()
        ses: Session = Session.query.filter_by(code=req["session"]["code"]).first()

        if ses is None:
            raise NotFound("Session does not exist")

        duplicate_name_user: User = User.query.filter_by(name=req["user"]["name"], session_id=ses.id).first()
        if duplicate_name_user is not None:
            raise Conflict("A user with that name already exists")

        # Create monopoly-user object
        user = User(
            session_id=ses.id,
            money=0,
            name=req["user"]["name"],
            isHost=False,
            socketConnection=User.generate_socket_connection_string()
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
                "socketConnection": user.socketConnection,
            }
        }, 201
