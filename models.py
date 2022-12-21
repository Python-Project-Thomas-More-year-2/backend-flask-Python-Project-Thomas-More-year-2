from flask_socketio import disconnect, emit
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.exceptions import Unauthorized

from helpers.generate_random_string import generate_random_string

db = SQLAlchemy()


class Session(db.Model):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    code = Column(String(7), nullable=False)
    startCapital = Column(Integer, nullable=False)
    goReward = Column(Integer, nullable=False)
    started = Column(Boolean, nullable=False, default=False)
    users = relationship("User")


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("session.id"), nullable=True)
    money = Column(Integer, nullable=False)
    name = Column(db.String(15), nullable=False)
    isHost = Column(Boolean, nullable=False)
    socketConnection = Column(db.String(256), unique=True)
    socketSessionId = Column(String, nullable=True, unique=True)
    session = relationship("Session", back_populates="users")

    def assert_is_host(self):
        if not self.isHost:
            raise Unauthorized("You are not the host")

    def disconnect_socket(self):
        if self.socketSessionId is not None:
            disconnect(sid=self.socketSessionId, namespace="/")

    def emit_to_session(self, event: str, data: dir):
        u: User
        for u in User.query.filter_by(session_id=self.session_id).all():
            if u.socketSessionId is not None:
                emit(event, data, to=u.socketSessionId, namespace="/")

    def emit_balance_update(self):
        self.emit_to_session('user-balance-update', {"user": {"id": self.id}})

    def emit(self, event: str, data: dir):
        if self.socketSessionId is not None:
            emit(event, data, to=self.socketSessionId, namespace="/")

    @staticmethod
    def generate_socket_connection_string() -> str:
        while True:
            rand = generate_random_string(256)
            if User.query.filter_by(socketConnection=rand).first() is None:
                break

        return rand
