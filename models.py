from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.exceptions import Unauthorized

db = SQLAlchemy()


class Session(db.Model):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    code = Column(String(7), nullable=False)
    startCapital = Column(Integer, nullable=False)
    seeOthersBalance = Column(Boolean, nullable=False)
    goReward = Column(Integer, nullable=False)
    freeParkingMoney = Column(Integer, nullable=False)
    freeParking = Column(Boolean, nullable=False)
    users = relationship("User")


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("session.id"), nullable=True)
    money = Column(Integer, nullable=False)
    name = Column(db.String(15), nullable=False)
    isHost = Column(Boolean, nullable=False)
    isBank = Column(Boolean, nullable=False)
    socketSessionId = Column(String, nullable=True, unique=True)
    session = relationship("Session", back_populates="users")

    def assert_is_host(self):
        if not self.isHost:
            raise Unauthorized("You are not the host")
