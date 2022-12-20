from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource

from helpers.get_user_by_session import get_user_by_session
from models import Session, User, db

schema_post = {
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

class GameGo(Resource):
    @staticmethod
    @expects_json(schema_post)
    def post():
        req = request.get_json()

        user = get_user_by_session(session, throw_unauthorized=True)

        user.assert_is_host()

        u = User.query.filter_by(id=req["user"]["id"], session_id=user.session_id).first()

        u.money += u.session.goReward
        db.session.commit()

        if u.session.seeOthersBalance:
            user.emit_to_session('money change', u.money)
        else:
            user.emit('money change', u.money)

        return {}, 200