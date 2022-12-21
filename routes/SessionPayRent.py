from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource
from werkzeug.exceptions import Conflict

from helpers.get_user_by_session import get_user_by_session
from models import User, db, Transaction

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
                    "type": "integer"
                }
            },
            "required": ["amount"],
        },
    },
    "required": ["user", "transaction"],
}
schema_put = {
    "type": "object",
    "properties": {
        "transaction": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                }
            },
            "required": ["id"],
        },
    },
    "required": ["transaction"],
}

class SessionPayRent(Resource):
    @staticmethod
    @expects_json(schema_post)
    def post():
        req = request.get_json()

        user = get_user_by_session(session, throw_unauthorized=True)

        u = User.query.filter_by(id=req["user"]["id"], session_id=user.session_id).first()

        if u is None:
            raise Conflict("User does not exist")

        if not u.session.started:
            raise Conflict("Session has not started yet")

        t = Transaction(
            request_sender_id = user.id,
            request_payer_id = req["user"]["id"],
            amount = req["transaction"]["amount"]
        )
        db.session.add(t)
        db.session.commit()

        u.emit_to_session('transaction-requested-rent', {
                "transaction":t.to_object()
            })

        return {}, 200

    @staticmethod
    @expects_json(schema_put)
    def put():
        req = request.get_json()

        #Check if the user is the transaction.request_payer of the given transaction.id
        t = Transaction.query.filter_by(id=req["transaction"]["id"]).first()
        u = User.query.filter_by(id=t.request_payer_id).first()

        if t is None:
            raise Conflict("Wrong user")

        #Check if user has enough money
        if u.money < t.amount:
            raise Conflict("User does not have enough money to afford this transaction")
        
        u.money -= t.amount
        db.session.commit()

       # Respond
        return {}, 200