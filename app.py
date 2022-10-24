from flask import Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship

app = Flask(__name__)
api = Api(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@127.0.0.1:5432/application"
db.init_app(app)


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("session.id"), nullable=True)
    money = Column(Integer, nullable=False)
    name = Column(db.String(15), nullable=False)
    isHost = Column(Boolean, nullable=False)
    isBank = Column(Boolean, nullable=False)
    socketSessionId = Column(Integer, nullable=True, unique=True)


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


with app.app_context():
    db.create_all()


class HelloWorld(Resource):
    @staticmethod
    def get():
        return {"value": 'Hello World!'}


api.add_resource(HelloWorld, '/')

if __name__ == "__main__":
    app.run(debug=True)
