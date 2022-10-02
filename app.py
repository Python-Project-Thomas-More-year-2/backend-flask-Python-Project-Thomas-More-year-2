from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    @staticmethod
    def get():
        return {"value": 'Hello World!'}


api.add_resource(HelloWorld, '/')

if __name__ == "__main__":
    app.run(debug=True)
