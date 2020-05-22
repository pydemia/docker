from alibi.datasets import fetch_imagenet
from alibi.explainers import AnchorImage
import dill
import tensorflow as tf
import numpy as np

print('tensorflow: ', tf.__version__)


# model = tf.saved_model.load('../predictor/mobilenet_saved_model')
#model = tf.keras.models.load_model('../predictor/mobilenet_saved_model')
model = tf.keras.models.load_model('./mobilenet_saved_model')



predict_fn = lambda x: model.predict(x)
kwargs = {'n_segments': 15, 'compactness': 20, 'sigma': .5}
image_shape = (224, 224, 3)


explainer = AnchorImage(
    predict_fn,
    image_shape,
    segmentation_fn='slic',
    segmentation_kwargs=kwargs,
    images_background=None,
)


categories = ['Persian cat', 'volcano', 'strawberry', 'jellyfish', 'centipede']
full_data = []
full_labels = []
for category in categories:
    data, labels = fetch_imagenet(
        category,
        nb_images=10,
        target_size=image_shape[:2],
        seed=0,
        return_X_y=True,
    )
    full_data.append(data)
    full_labels.append(labels)

full_data = np.concatenate(full_data)
full_labels = np.concatenate(full_labels)


# data.shape
# explainer.fit(
#     fetch_imagenet
# )

# Clear explainer predict_fn as its a lambda and will be reset when loaded
explainer.predict_fn = None
with open("./mobilenet_explainer.dill", 'wb') as f:
    dill.dump(explainer, f)
