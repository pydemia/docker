import modai
import os
import json
import numpy as np
import uuid

import base64
import cv2


def _load_image_as_str(filename):
    img_bgr = cv2.imread(filename, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    string = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    return string

# docker cp ../src/microorganism_13/model/frozen_inference_graph.pb mo:/models/microorganism
# docker cp ar118.json mo:/tmp/
# with open('/tmp/ar118.json') as f:
#     input_json = json.load(f)['instances']

# _img = input_json[0]['image_bytes']


def predict(input_json, model_path):

    # model_path_n_file='microorganism_13/model/frozen_inference_graph.pb'
    # input_path='microorganism_13/dataset/0614/A'
    # output_path='microorganism_13/dataset/0614/A_infer'
    # log_name='microorganism_13/logging/progress_infer.log'

    # image_bytes: b64_string_images
    # input_json: [{'image_bytes': ..., 'key': ...}, ...]

    foldername = str(uuid.uuid4())
    input_savepath = os.path.join('/tmp', foldername)
    os.makedirs(input_savepath, exist_ok=True)

    for _item in input_json:
        _key = _item['key']
        _img = _item['image_bytes']
        #_img_b64 = _img.encode('base64')
        jpg_original = base64.b64decode(_img)  # it will ignore extraneous padding
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)

        filename = str(_key)
        filepath = os.path.join(input_savepath, filename + '.jpg')
        cv2.imwrite(filepath, img)
        print('input saved:', img.shape)

    model_path_n_file = model_path
    input_path = input_savepath
    output_path = input_savepath + '_output'
    output_file_path = os.path.join(output_path,'annotations')
    output_image_path = os.path.join(output_path,'images')
    log_name = '/tmp/progress_infer.log'

    # os.makedirs(output_path, exist_ok=True)
    # os.makedirs(output_file_path, exist_ok=True)
    # os.makedirs(output_image_path, exist_ok=True)

    # to enforce CPU only: BEFORE import `tensorflow`
    os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
    modai.mo_inference(
        model_path_n_file=model_path_n_file,
        input_path=[input_path],
        output_file_path=output_file_path,
        output_image_path=output_image_path,
        progress_path_n_file=log_name,
        gpu_id='-1',  # '-1' for CPU
    )

    result = []
    for _item in input_json:
        _key = _item['key']
        _img = _item['image_bytes']
        # INPUT
        #  - images: '${INPUT_PATH}/ar (12).jpg'
        # OUTPUT
        #  - annotations: '${INPUT_PATH}_output/annotations/ar (12)_result.xml'
        #  - images: '${INPUT_PATH}_output/images/ar (12)_result.jpg'
        filename = str(_key)
        annot_file = os.path.join(output_file_path, filename + '_result.xml')
        image_file = os.path.join(output_image_path, filename + '_result.jpg')
        with open(annot_file, 'r') as annot:
            annot_string = annot.read()
        image_string = _load_image_as_str(image_file)
        result.append(
            {
                'key': str(_key),
                'annotation': annot_string,
                'image': image_string,
            }
        )

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