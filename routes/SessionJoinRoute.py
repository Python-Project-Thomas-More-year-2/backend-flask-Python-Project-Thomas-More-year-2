from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource
from werkzeug.exceptions import NotFound

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
        session: Session = Session.query.filter_by(code=req["session"]["code"]).first()

        if session is None:
            raise NotFound("Session does not exist")

        # Create monopoly-user object
        user = User (
            session_id=ses.id,
            money=0,
            name=req["user"]["name"],
            isHost=False,
            isBank=False,
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




        


            
            
