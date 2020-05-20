import kfserving
from PIL import Image
import logging
import numpy as np
import os
import json
import argparse

import base64
from io import BytesIO


import tensorflow as tf
print('tensorflow: ', tf.__version__)

# mobnet = tf.keras.applications.mobilenet
# pre_processing_fn = mobnet.preprocess_input
# post_processing_fn = mobnet.decode_predictions

# model = mobnet.MobileNet(weights='imagenet')
# model.save('./mobilenet_saved_model', save_format='tf')

# image_saved_path = tf.keras.utils.get_file(
#     "grace_hopper.jpg",
#     "https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg",
# )


# Preprocessing -----------------------------
def _load_b64_string_to_img(b64_byte_string):
        image_bytes = base64.b64decode(image_byte_string)
        image_data = BytesIO(image_bytes)
        img = Image.open(image_data)
        return img


def preprocess_fn(instance):
    img = _load_b64_string_to_img(instance['image_bytes'])
    img_resized = img.resize([224, 224], resample=Image.BILINEAR)
    img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
    # The inputs pixel values are scaled between -1 and 1, sample-wise.
    x = tf.keras.applications.mobilenet.preprocess_input(
        img_resized,
        data_format='channels_last',
    )
    #x = np.expand_dims(x, axis=0)
    return x


# Postprocessing ----------------------------
def postprocess_fn(pred):
    decoded = tf.keras.applications.mobilenet.decode_predictions(
        [pred], top=5
    )
    return decoded


class ImageTransformer(kfserving.KFModel):
    def __init__(self, name: str, predictor_host: str):
        super().__init__(name)
        self.predictor_host = predictor_host

    def preprocess(self, inputs: Dict) -> Dict:
        return {'instances': [preprocess_fn(instance) for instance in inputs['instances']]}

    def postprocess(self, inputs: List) -> List:
        return postprocess_fn(inputs)


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