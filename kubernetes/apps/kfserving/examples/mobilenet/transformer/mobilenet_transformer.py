import kfserving
from PIL import Image
import logging
import numpy as np
import pandas as pd
import os
import json
import argparse

import base64
from io import BytesIO


logging.basicConfig(level=kfserving.constants.KFSERVING_LOGLEVEL)

import tensorflow as tf
logging.info('tensorflow: {}'.format(tf.__version__))

# mobnet = tf.keras.applications.mobilenet
# pre_processing_fn = mobnet.preprocess_input
# post_processing_fn = mobnet.decode_predictions

# model = mobnet.MobileNet(weights='imagenet')
# model.save('./mobilenet_saved_model', save_format='tf')

# image_saved_path = tf.keras.utils.get_file(
#     "grace_hopper.jpg",
#     "https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg",
# )


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def _serialize(jsonlike_dict):
    return json.dumps(jsonlike_dict, cls=NumpyEncoder)


# Preprocessing -----------------------------
def _load_b64_string_to_img(b64_byte_string):
        image_bytes = base64.b64decode(b64_byte_string)
        image_data = BytesIO(image_bytes)
        img = Image.open(image_data)
        return img


def preprocess_fn(instance):
    img = _load_b64_string_to_img(instance['input_1'])
    logging.info(img)
    img_resized = img.resize([224, 224], resample=Image.BILINEAR)
    img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
    # The inputs pixel values are scaled between -1 and 1, sample-wise.
    x = tf.keras.applications.mobilenet.preprocess_input(
        img_array,
        data_format='channels_last',
    )
    logging.info(x)
    #x = np.expand_dims(x, axis=0)
    # x = _serialize(x)
    return x.tolist()


# Postprocessing ----------------------------
def postprocess_fn(pred):
    pred_array = np.array(pred)
    # if len(pred_array.shape) < 2:
    #   pred_array = np.expand_dims(pred_array, axis=0)
    decoded = tf.keras.applications.mobilenet.decode_predictions(
        pred_array, top=5
    )
    logging.info(decoded)
    return decoded



class ImageTransformer(kfserving.KFModel):
    def __init__(self, name: str, predictor_host: str):
        super().__init__(name)
        self.predictor_host = predictor_host

    def preprocess(self, inputs):
        return {'instances': [preprocess_fn(i) for i in inputs['instances']]}

    def postprocess(self, outputs):
        # outputs: {"predictions": ndarray_as_list}
        # return outputs
        # return {'predictions': [postprocess_fn(o) for o in outputs['predictions']]}
        return {'predictions': postprocess_fn(outputs['predictions'])}


parser = argparse.ArgumentParser(parents=[kfserving.kfserver.parser])
parser.add_argument(
    '--model_name', default='model',
    help='The name that the model is served under.',
)
parser.add_argument(
    '--predictor_host',
    required=True,
    help='The URL for the model predict function',
)
args, _ = parser.parse_known_args()


if __name__ == "__main__":
    transformer = ImageTransformer(
        args.model_name,
        predictor_host=args.predictor_host,
    )
    kfserver = kfserving.KFServer()
    kfserver.start(models=[transformer])
