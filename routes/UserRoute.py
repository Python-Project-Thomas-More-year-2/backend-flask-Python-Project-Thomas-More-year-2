from flask import session
from flask_restful import Resource

from helpers.get_user_by_session import get_user_by_session


class UserRoute(Resource):
    @staticmethod
    def get():
        user = get_user_by_session(session, throw_unauthorized=True)

        return {
                   "user": {
                       "id": user.id,
                       "session_id": user.session_id,
                       "money": user.money,
                       "name": user.name,
                       "isHost": user.isHost,
                       "isBank": user.isBank
                   }
               }, 200
