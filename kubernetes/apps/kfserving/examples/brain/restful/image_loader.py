#!/usr/bin/python3

import os
import json
import argparse

import base64
import cv2

def _load_image_as_str(filename, output):
    img = cv2.imread(filename)
    string = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    # string = base64.b64encode(img).decode('utf8')

    res = {
        'instances': [
            {'image_bytes': string, 'key': '1'}
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
parser.add_argument('--output', '-o', type=str, required=True)


if __name__ == '__main__':
    ARGS = parser.parse_args()
    INPUT = ARGS.input
    OUTPUT = ARGS.output
    _load_image_as_str(INPUT, OUTPUT)