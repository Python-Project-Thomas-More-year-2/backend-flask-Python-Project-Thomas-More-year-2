from datetime import timedelta

from flask import Flask, make_response, jsonify, session, request
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO, emit
from jsonschema import ValidationError

from helpers.get_user_by_session import get_user_by_session
from models import db, User
from routes.HelloWorld import HelloWorld
from routes.SessionJoinRoute import SessionJoinRoute
from routes.SessionPlayerList import SessionPlayerList
from routes.SessionRoute import SessionRoute
from routes.UserRoute import UserRoute

app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

CORS(app, resource={"*": {"origins": "*"}}, supports_credentials=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@127.0.0.1:5432/application"
app.config["SECRET_KEY"] = "A_SECRET_KEY"  # Change in build
app.permanent_session_lifetime = timedelta(days=1)

db.init_app(app)

with app.app_context():
    db.create_all()

api.add_resource(HelloWorld, '/')
api.add_resource(SessionRoute, '/session')
api.add_resource(SessionPlayerList, '/session/playerlist')
api.add_resource(SessionJoinRoute, '/session/join')
api.add_resource(UserRoute, '/user')


# https://pypi.org/project/flask-expects-json/#:~:text=register()%3A%0A%20%20%20%20return-,Error%20handling,-On%20validation%20failure
@app.errorhandler(400)
def bad_request(error):
    if isinstance(error.description, ValidationError):
        original_error = error.description
        return make_response(jsonify({'error': original_error.message}), 400)
    # handle other "Bad Request"-errors
    return error


@socketio.on('connect')
def connect():
    # No implementation
    pass


@socketio.on("auth")
def auth(json):
    if "socketConnection" not in json:
        emit("auth-res", {
            "error": "invalid data send"
        })
        return

    socket_connection = json.get("socketConnection")
    # find user with the given code
    user = User.query.filter_by(socketConnection=socket_connection).first()

    if user is None:
        emit("auth-res", {
            "error": "no user found with the given socket_connection"
        })
        return

    # user exists

    # delete other connection if exist
    user_prev_connection: User | None = User.query.filter_by(socketSessionId=request.sid).first()
    if user_prev_connection is not None:
        user_prev_connection.socketSessionId = None
        db.session.commit()

    # Add socket-id to user
    user.socketSessionId = request.sid
    db.session.commit()

    u: User
    for u in User.query.filter_by(session_id=user.session_id).all():
        emit("user-connect", {
            "user": {
                "id": user.id,
            }
        }, to=u.socketSessionId)

    emit("auth-res", {
        "message": "connected to session"
    })


@socketio.on('disconnect')
def disconnect():
    user = get_user_by_session(session)

    if user is not None:
        user.socketSessionId = None
        db.session.commit()


if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app, debug=True)
