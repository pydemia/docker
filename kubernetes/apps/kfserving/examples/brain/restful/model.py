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