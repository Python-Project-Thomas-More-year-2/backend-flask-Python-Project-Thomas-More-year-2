from flask import session
from flask_expects_json import expects_json
from flask_restful import Resource

from helpers.get_user_by_session import get_user_by_session
from models import Session

schema_post = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "money": {
                    "type": "integer"
                }
            },
            "required": ["id"],
        },
    },
    "required": ["user"],
}

class GameStart(Resource):
    @staticmethod
    @expects_json(schema_post)
    def post():
        user = get_user_by_session(session, throw_unauthorized=True)

        user.assert_is_host()

        if user is None:
            return {}, 404

        user.money += Session.goReward

        if Session.seeOthersBalance:
            user.emit_to_session()
        else:
            user.emit()

        user.update({
            "money": user.money
        })
        
        return {}, 200

        

        


        