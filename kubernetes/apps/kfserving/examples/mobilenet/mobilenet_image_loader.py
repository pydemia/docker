#!/usr/bin/python3

import os
import json
import argparse

import base64
import cv2


def _load_image_as_str(filename, output, image_type='rgb', output_type='numpy'):

    if image_type == 'rgb':
        img_bgr = cv2.imread(filename, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    else:
        img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    
    if output_type == 'b64':
        string = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    elif output_type == 'numpy':
        string = str(img)
    # string = base64.b64encode(img).decode('utf8')

    res = {
        'instances': [
            {'input_1': string}
        ]
    }
    # savepath = os.path.join(output, filename + '.json')
    savepath = output
    with open(savepath, 'w') as f:
        #json.dumps({"image": base64.b64encode(imdata).decode('ascii')})
        #json.dump(res, f, ensure_ascii=False)
        json.dump(res, f, ensure_ascii=False)
    print('saved:', savepath)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--input', '-i', type=str, required=True)
parser.add_argument('--input_type', '-it', type=str,
                    default='rgb', choices=['rgb', 'grayscale'])
parser.add_argument('--output', '-o', type=str, required=True)
parser.add_argument('--output_type', '-ot', type=str, default='numpy', choices=['b64', 'numpy'])


if __name__ == '__main__':
    ARGS = parser.parse_args()
    INPUT = ARGS.input
    INPUT_TYPE = ARGS.input_type
    OUTPUT = ARGS.output
    OUTPUT_TYPE = ARGS.output_type
    _load_image_as_str(INPUT, OUTPUT, image_type=INPUT_TYPE, output_type=OUTPUT_TYPE)
