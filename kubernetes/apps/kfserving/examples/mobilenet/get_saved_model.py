# /usr/bin/env python

import tensorflow as tf

print('tensorflow: ', tf.__version__)

mobnet = tf.keras.applications.mobilenet

model = mobnet.MobileNet(weights='imagenet')
model.save('./mobilenet_saved_model.pb', save_format='tf')
preprocessing = mobnet.preprocess_input
post_processing = mobnet.decode_predictions
