from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource
from werkzeug.exceptions import Unauthorized, BadRequest

from models import db, User

schema_delete = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                }
            },
            "required": ["id"],
        },
    },
    "required": ["user"],
}

class SessionPlayerList(Resource):
    @staticmethod
    @expects_json(schema_delete)
    def delete():
        # Get JSON-data body from request
        req = request.get_json()

        if session.get("user_id") is None:
            raise Unauthorized("User has no connected session")

        user = User.query.filter_by(id=session.get("user_id")).first()     

        if user is None:
            session.pop("user_id")
            raise Unauthorized("User has no connected session")

        if not user.isHost:
            raise Unauthorized("You are not the host")

        if user.id == req["user"]["id"]:
            raise BadRequest("You can not kick yourself")
            
        User.query.filter_by(id=req["user"]["id"], session_id=user.session_id).delete()
        db.session.commit()

        users_db = User.query.filter_by(session_id=user.session_id).all()
        users = []

        for u in users_db:
            users.append({
                       "id": u.id,
                       "session_id": u.session_id,
                       "money": u.money,
                       "name": u.name,
                       "isHost": u.isHost,
                       "isBank": u.isBank
                   })
        
        return users, 200