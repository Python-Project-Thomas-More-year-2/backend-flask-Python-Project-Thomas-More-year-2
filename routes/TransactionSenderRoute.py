from flask import session
from flask_restful import Resource

from helpers.get_user_by_session import get_user_by_session
from models import Transaction


class TransactionSenderRoute(Resource):
    @staticmethod
    def get():
        user = get_user_by_session(session, throw_unauthorized=True)

        t: Transaction
        return [t.to_object() for t in user.transaction_sender], 200
