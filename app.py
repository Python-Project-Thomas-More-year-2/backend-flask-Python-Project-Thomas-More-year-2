from flask import Flask
from flask_restful import Api, Resource

from models import db

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@127.0.0.1:5432/application"
db.init_app(app)

with app.app_context():
    db.create_all()


class HelloWorld(Resource):
    @staticmethod
    def get():
        return {"value": 'Hello World!'}


api.add_resource(HelloWorld, '/')

if __name__ == "__main__":
    app.run(debug=True)
