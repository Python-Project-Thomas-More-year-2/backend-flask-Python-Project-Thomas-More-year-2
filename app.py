from datetime import timedelta

from flask import Flask, make_response, jsonify
from flask_cors import CORS
from flask_restful import Api
from jsonschema import ValidationError

from models import db
from routes.HelloWorld import HelloWorld
from routes.SessionRoute import SessionRoute

app = Flask(__name__)
api = Api(app)

CORS(app, resource={"*": {"origins": "*"}}, supports_credentials=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@127.0.0.1:5432/application"
app.config["SECRET_KEY"] = "A_SECRET_KEY"  # Change in build
app.permanent_session_lifetime = timedelta(days=1)

db.init_app(app)

with app.app_context():
    db.create_all()

api.add_resource(HelloWorld, '/')
api.add_resource(SessionRoute, '/session')


# https://pypi.org/project/flask-expects-json/#:~:text=register()%3A%0A%20%20%20%20return-,Error%20handling,-On%20validation%20failure
@app.errorhandler(400)
def bad_request(error):
    if isinstance(error.description, ValidationError):
        original_error = error.description
        return make_response(jsonify({'error': original_error.message}), 400)
    # handle other "Bad Request"-errors
    return error


if __name__ == "__main__":
    app.run(debug=True)
