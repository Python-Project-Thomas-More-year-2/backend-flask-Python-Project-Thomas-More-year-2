from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource
from flask_socketio import disconnect
from werkzeug.exceptions import BadRequest

from helpers.get_user_by_session import get_user_by_session
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

        user = get_user_by_session(session, throw_unauthorized=True)

        user.assert_is_host()

        if user.id == req["user"]["id"]:
            raise BadRequest("You can not kick yourself")

        query = User.query.filter_by(id=req["user"]["id"], session_id=user.session_id)

        kicked_users = query.all()

        for u in kicked_users:
            if u.socketSessionId is not None:
                disconnect(sid=u.socketSessionId, namespace="/")

        query.delete()
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

        for u in kicked_users:
            user.emit_to_session("user-disconnect", {
                "user": {
                    "id": u.id,
                }
            })

        return users, 200

    @staticmethod
    def get():
        user = get_user_by_session(session, throw_unauthorized=True)

        users_db = User.query.filter_by(session_id=user.session_id).all()
        users = []

        for u in users_db:
            users.append({
                "id": u.id,
                "session_id": u.session_id,
                "money": u.money,
                "name": u.name,
                "isHost": u.isHost,
                "isBank": u.isBank,
                "socketConnection": u.socketSessionId,
            })

        return users, 200
