from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource
from werkzeug.exceptions import Conflict

from helpers.get_user_by_session import get_user_by_session
from models import User, db

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
        "transaction": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "integer",
                    "minimum": 1,
                },
            },
            "required": ["amount"],
        },
    },
    "required": ["user", "transaction"],
}


class BankMoney(Resource):
    @staticmethod
    @expects_json(schema_post)
    def post():
        req = request.get_json()

        user = get_user_by_session(session, throw_unauthorized=True)

        user.assert_is_host()

        u = User.query.filter_by(
            id=req["user"]["id"], session_id=user.session_id).first()

        if u is None:
            raise Conflict("User does not exist")

        if not u.session.started:
            raise Conflict("Session has not started yet")

        u.money += req["transaction"]["amount"]
        db.session.commit()

        user.emit_balance_update()

        return {}, 200
