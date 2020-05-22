# Brain

## List-up Requirements

* Versions
  * TF Version
  * NVIDIA Runtime Version
    * CUDA Version
    * cuDNN Version
  * Python Version

* Any Package Dependencies


## Build Container Image

Get Docker first:
```sh
TF_VERSION=1.11.0
docker pull tensorflow/serving:$TF_VERSION-py3
# docker pull tensorflow/serving:$TF_VERSION-gpu-py3

docker run --rm --name=tf_serving -d  -p 8500:8500/tcp -p 8501:8501/tcp tensorflow/serving:$TF_VERSION
docker cp tf_serving:/usr/bin/tf_serving_entrypoint.sh ./
```

`tf_serving_entrypoint.sh`:
```sh
#!/bin/bash 

tensorflow_model_server --port=8500 --rest_api_port=8501 --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} "$@"
```

* ~~`8500`: `gRPC`~~
* **`8501`: `HTTP`**

Get Docker base:
```sh
TF_VERSION=1.11.0
docker pull tensorflow/tensorflow:$TF_VERSION-py3
# docker pull tensorflow/tensorflow:$TF_VERSION-gpu-py3

docker run --rm --name tf_base -d  -p 6006:6006/tcp -p 8888:8888/tcp tensorflow/tensorflow:$TF_VERSION-py3

# COPY pkg to container
docker cp ./src/skipc_microorganism_detection_model tf_base:/tmp/skipc_microorganism_detection_model
```

Inside Container:
```sh
docker exec -it tf_base /bin/sh -c "[ -e /bin/bash ] && /bin/bash || /bin/sh"
cd /tmp/skipc_microorganism_detection_model
python setup.py install
#error: Keras-Applications 1.0.5 is installed but keras-applications==1.0.4 is required by {'keras'}

# Additional Packages
apt-get update && \
apt-get install -y libsm6 libxext6 libxrender-dev libglib2.0-0

pip install contextlib2 opencv-python Cython
# After install Cython
pip install pycocotools lxml

apt-get clean
```

Outside Container:
```sh
docker commit tf_base microorganism:v0.1
```

## Get info: `model.predict`

* `predict: modai.mo_inference(...)`

```sh
import modai
import os

model_path_n_file='microorganism_13/model/frozen_inference_graph.pb'
input_path='microorganism_13/dataset/0614/A'
output_path='microorganism_13/dataset/0614/A_infer'
log_name='microorganism_13/logging/progress_infer.log'

modai.mo_inference(model_path_n_file=model_path_n_file,
		   input_path=[input_path],
		   output_file_path=os.path.join(output_path,'annotations'),
		   output_image_path=os.path.join(output_path,'images'),
		   progress_path_n_file=log_name,
		   gpu_id='0')
```
* Class:
  * `modai`
* Method:
  * `.mo_inference(...)`
* Args:
  * model_path_n_file: `frozen_inference_graph.pb`
  * input_path: `$input_path`
  * output_file_path: `$output_path/annotations`
  * output_image_path: `$output_path/images`
  * log_name: `progress.log`
  * gpu_id: `0`

---
### 이식성 판단

재작성 필요한 부분
* 모델 입출력 `file -> json(& REST)`: Input, Output, ~~Logging~~(나중에 생각)

---
### WEB APP으로 변경

https://github.com/Azure-App-Service/flask-docker

* flask: RESTful web framework for python
* docker

```sh
git clone https://github.com/Azure-App-Service/flask-docker
cp ./flask-docker/sshd_config ./restful/
cp ./flask-docker/init.sh ./restful/
cp ./flask-docker/Dockerfile ./restful/Dockerfile_base
# cd restful
```

Show `Dockerfile(->Dockerfile_base)`:
```Dockerfile
FROM python:3.6.1

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
	&& apt-get install -y --no-install-recommends openssh-server \
	&& echo "$SSH_PASSWD" | chpasswd 

COPY sshd_config /etc/ssh/
COPY init.sh /usr/local/bin/
	
RUN chmod u+x /usr/local/bin/init.sh
EXPOSE 5000 2222
ENTRYPOINT ["init.sh"]
```

Show `runserver.py`:
```py
"""
This script runs the flaskwebapp application using a development server.
"""

from os import environ
from flaskwebapp import app

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
```

`model.py`
```py
import modai
import os
import json
import numpy as np
import uuid

import base64
import json
import cv2


def _load_image_as_str(filename):
    img = cv2.imread(filename)
    string = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    return string


def predict(input_json, model_path):

    # model_path_n_file='microorganism_13/model/frozen_inference_graph.pb'
    # input_path='microorganism_13/dataset/0614/A'
    # output_path='microorganism_13/dataset/0614/A_infer'
    # log_name='microorganism_13/logging/progress_infer.log'

    # INPUT: b64_string_images
    input_images = input_json['images']

    foldername = str(uuid.uuid4())
    input_path = os.path.join('/tmp', foldername)
    os.makedirs(input_path, exist_ok=True)

    input_files = []
    for i, _img in enumerate(input_images):
        jpg_original = base64.b64decode(_img)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)

        filename = 'img_' + str(i)
        filepath = os.path.join(input_path, filename)
        cv2.imwrite(filepath, img)
        input_files.append(filename)

    model_path_n_file = model_path
    input_path = savepath
    output_path = savepath + '_output'
    output_file_path = os.path.join(output_path,'annotations')
    output_image_path = os.path.join(output_path,'images')
    log_name = '/tmp/progress_infer.log'

    modai.mo_inference(
        model_path_n_file=model_path_n_file,
        input_path=[input_path],
        output_file_path=os.path.join(output_path,'annotations'),
        output_image_path=os.path.join(output_path,'images'),
        progress_path_n_file=log_name,
        gpu_id='0',
    )

    result = {}
    for i, _img in enumerate(input_images):
        # INPUT
        #  - images: '${INPUT_PATH}/ar (12).jpg'
        # OUTPUT
        #  - annotations: '${INPUT_PATH}_output/annotations/ar (12)_result.xml'
        #  - images: '${INPUT_PATH}_output/images/ar (12)_result.jpg'
        annot_file = os.path.join(output_file_path, input_files + '_result.xml')
        image_file = os.path.join(output_image_path, input_files + '_result.jpg')
        with open(annot_file, 'r') as annot:
            annot_string = annot.read()
        image_string = _load_image_as_str(image_file)
        result[str(i)] = {
            'annotation': annot_string,
            'image': image_string,
        }

    # result format
    # {
    #    "0": {
    #       "annotation": "<xml-string>",
    #       "image": "<img-b64-string>"
    #    },
    #    "1": {
    #       "annotation": "<xml-string>",
    #       "image": "<img-b64-string>"
    #    },
    #    ...
    # }

    return result
```

Change `runserver.py`:
```py
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
    app.run(debug=True, host='0.0.0.0', port=8501)
```

Create a new `Dockerfile` for `HTTP`:
```Dockerfile
FROM microorganism:v0.1

RUN mkdir -p /models
WORKDIR /tmp/skipc_microorganism_detection_model

RUN pip install \
    contextlib2 opencv-python Flask flask-restful jsonify

COPY init.sh /usr/local/bin/
	
RUN chmod u+x /usr/local/bin/init.sh
EXPOSE 8500
ENTRYPOINT ["init.sh"]
```

```sh
docker build . -t pydemia/microorganism:v0.1.0-http
docker tag pydemia/microorganism:v0.1.0-http gcr.io/ds-ai-platform/microorganism:v0.1.0-http
docker push gcr.io/ds-ai-platform/microorganism:v0.1.0-http
```
---
## Next: Write `gRPC` using flask RESTful code
<https://github.com/biplabpokhrel/grpc-flask-tutorial>
<https://medium.com/@biplav.nep/grpc-using-flask-restful-code-2ed5607ae9a>


```sh
docker pull znly/protoc:latest
docker run --rm -v $(pwd):$(pwd) -w $(pwd) znly/protoc --plugin=protoc-gen-grpc=/usr/bin/grpc_python_plugin --python_out=./messages/  --grpc_out=./messages/  --proto_path=./protobuf ./protobuf/*.proto
```

Create a new `Dockerfile`, for `HTTP` and `gRPC`:
```Dockerfile
FROM microorganism:v0.1

WORKDIR /tmp/skipc_microorganism_detection_model
RUN apt-get update && \
    apt-get install -y \
    libstdc++, libc6-compat

RUN pip install \
    contextlib2 opencv-python Flask flask-restful jsonify

ENV GRPC_PYTHON_VERSION 1.15.0
RUN pip install \
    grpcio==${GRPC_PYTHON_VERSION} \
    grpcio-tools==${GRPC_PYTHON_VERSION}


COPY init.sh /usr/local/bin/
	
RUN chmod u+x /usr/local/bin/init.sh
EXPOSE 8500 8501
ENTRYPOINT ["init.sh"]
```

---

```sh
cd flask-docker
docker cp -r ./flaskwebapp tf_base:/code/
docker cp ./requirements.txt tf_base:/code/
docker cp ./init.sh tf_base:/usr/local/bin/
```

Inside Container:
```sh
docker exec -it tf_base /bin/sh -c "[ -e /bin/bash ] && /bin/bash || /bin/sh"
cd /tmp/skipc_microorganism_detection_model

```

---

```sh
python -m image_loader -i ./ar\ \(118\).jpg -o ./ar118.json

docker cp ../src/microorganism_13/model/frozen_inference_graph.pb mo:/models/microorganism
```

```sh
curl http://localhost:8501/v1/models/microorganism:predict -d '@./ar118.json'

MODEL_NAME=sklearn-iris
INPUT_PATH=@./iris-input.json
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH  
```

```ascii
Error from server: error when creating "microorganism.yaml": admission webhook "inferenceservice.kfserving-webhook-server.validator" denied the request: Exactly one of [Custom, ONNX, Tensorflow, TensorRT, SKLearn, XGBoost] must be specified in PredictorSpec
```


---
## Set private


## Deploy in KFServing


```sh
kubectl get ksvc microorganism-predictor-default -o yaml
kubectl get inferenceservice microorganism

MODEL_NAME=microorganism
INPUT_PATH=@./Project_TileScan_1.json
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
#sleep 20s
SERVICE_HOSTNAME=$(kubectl get inferenceservice ${MODEL_NAME} -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "
CLUSTER_IP      : $CLUSTER_IP
SERVICE_HOSTNAME: $SERVICE_HOSTNAME"
curl -m 960 -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH

curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH

curl -v \
    http://microorganism.default.35.223.25.173.xip.io/v1/models/microorganism:predict \
    -d '@./Project_TileScan_1.json' > ./Project_TileScan_1_result.json
```

```sh
$ kubectl apply -f microorganism_custom.yaml
inferenceservice.serving.kubeflow.org/microorganism created
```

"tensorflow": {
            "image": "tensorflow/serving",
            "defaultImageVersion": "1.14.0",
            "defaultGpuImageVersion": "1.14.0-gpu",
            "allowedImageVersions": [
               "1.11.0",
               "1.11.0-gpu", 
               "1.12.0",
               "1.12.0-gpu",
               "1.13.0",
               "1.13.0-gpu",
               "1.14.0",
               "1.14.0-gpu"
            ]
        },
"microorganism": {
            "image": "gcr.io/ds-ai-platform/microorganism",
            "defaultImageVersion": "v0.1.0-http",
            "defaultGpuImageVersion": "v0.1.0-http-gpu",
            "allowedImageVersions": [
               "v0.1.0-http",
               "v0.1.0-http-gpu",
               "v0.1.0-http-grpc",
               "v0.1.0-http-grpc-gpu"
            ]
        },