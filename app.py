from datetime import timedelta

from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO, emit
from jsonschema import ValidationError

from models import db, User
from routes.GameGo import GameGo
from routes.GameMoneyFromBank import BankMoney
from routes.HelloWorld import HelloWorld
from routes.PropertyPurchase import PropertyPurchase
from routes.SessionJoinRoute import SessionJoinRoute
from routes.SessionPayRent import SessionPayRent
from routes.SessionPlayerList import SessionPlayerList
from routes.SessionRoute import SessionRoute
from routes.SessionStartRoute import SessionStartRoute
from routes.TransactionPayerRoute import TransactionPayerRoute
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
api.add_resource(GameGo, '/session/game/go')
api.add_resource(BankMoney, '/session/game/bank-money')
api.add_resource(SessionStartRoute, '/session/start')
api.add_resource(PropertyPurchase, '/session/game/property-purchase')
api.add_resource(TransactionPayerRoute, '/session/game/transacions/payer')
api.add_resource(SessionPayRent, '/session/game/pay-rent')


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
    user_prev_connection: User | None = User.query.filter_by(
        socketSessionId=request.sid).first()
    if user_prev_connection is not None:
        user_prev_connection.socketSessionId = None
        db.session.commit()

    # Add socket-id to user
    user.socketSessionId = request.sid
    db.session.commit()

    user.emit_to_session("user-connect", {
        "user": {
            "id": user.id,
        }
    })

    emit("auth-res", {
        "message": "connected to session"
    })


@socketio.on('disconnect')
def disconnect():
    user_prev_connection: User | None = User.query.filter_by(
        socketSessionId=request.sid).first()

    if user_prev_connection is None:
        return

    user_prev_connection.socketSessionId = None
    db.session.commit()

    user_prev_connection.emit_to_session("user-disconnect", {
        "user": {
            "id": user_prev_connection.id,
        }
    })


if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app, debug=True)
