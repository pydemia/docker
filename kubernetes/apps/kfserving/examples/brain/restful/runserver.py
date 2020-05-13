import os
from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource


app = Flask(__name__)
api = Api(app)


MODEL_NAME = 'microorganism'
MODEL_PATH = os.path.join('/model', MODEL_NAME)


class Serving(Resource):
    def post(self):
        args = parser.parse_args()

        # args['image']: image_byte (base64)
        input_images = {'input_path': args['image']}
        
        result = predict(input_images, MODEL_PATH)
        return result, 201

# URL: '/v1/model/MODEL_NAME/<string:predict>'
URL = os.path.join('/v1/model', MODEL_NAME, '<string:predict>')
api.add_resource(Serving, URL)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
