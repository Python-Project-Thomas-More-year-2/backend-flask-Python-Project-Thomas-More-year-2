from flask import session
from flask_restful import Resource
from werkzeug.exceptions import Conflict

from helpers.get_user_by_session import get_user_by_session
from models import db


class SessionStartRoute(Resource):
    @staticmethod
    def post():
        user = get_user_by_session(session, True)

        user.assert_is_host()

        if user.session.started:
            raise Conflict("Can not start session twice")

        user.session.started = True
        db.session.commit()

        user.emit_to_session("session-start", {})

        return {}, 204
