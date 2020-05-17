import os
from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource

import model

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
#parser.add_argument('image')

MODEL_NAME = 'microorganism'
MODEL_PATH = os.path.join('/models', MODEL_NAME)
# docker cp ../src/microorganism_13/model/frozen_inference_graph.pb mo:/models/microorganism

class Serving(Resource):
    def post(self, predict):
        # args = parser.parse_args()
        # args['image']: image_byte (base64)
        # input_images = {'input_path': args['image']}
        json_data = request.get_json(force=True)  #.encode('utf-8')

        # {
        #     'instances': [
        #         {'image_bytes': string, 'key': '1'}
        #     ]
        # }
        input_instances = json_data['instances']
        # input_images = json_data['instances'][0]['image_bytes']

        result = model.predict(input_instances, MODEL_PATH)
        return result, 201

# URL: '/v1/models/$MODEL_NAME/<string:predict>'
URL = os.path.join('/v1/models', MODEL_NAME + '<string:predict>')
api.add_resource(Serving, URL)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8501)
