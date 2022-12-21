from flask import session
from flask_restful import Resource
from models import Transaction
from helpers.get_user_by_session import get_user_by_session


class TransactionPayerRoute(Resource):
    @staticmethod
    def get():
        user = get_user_by_session(session, throw_unauthorized=True)

        t: Transaction
        return [t.to_object() for t in user.transaction_payer], 200
