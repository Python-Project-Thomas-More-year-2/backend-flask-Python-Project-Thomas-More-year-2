from flask import request, session
from flask_expects_json import expects_json
from flask_restful import Resource
from werkzeug.exceptions import Conflict, NotFound

from helpers.get_user_by_session import get_user_by_session
from models import User, db, Transaction


class SessionTransactionBank(Resource):
    @staticmethod
    def get():
        user = get_user_by_session(session, throw_unauthorized=True)

        user.assert_is_host()

        return [t.to_object() for t in Transaction.query.filter_by(request_sender_id=None).all()], 200
