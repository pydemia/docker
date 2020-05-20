from alibi.datasets import fetch_imagenet
from alibi.explainers import AnchorImage
import dill
import tensorflow as tf

print('tensorflow: ', tf.__version__)


model = tf.saved_model.load('../predictor/mobilenet_saved_model')



predict_fn = model.predict
kwargs = {'n_segments': 15, 'compactness': 20, 'sigma': .5}
image_shape = (224, 224, 3)


explainer = AnchorImage(
    predict_fn,
    image_shape,
    segmentation_fn='slic',
    segmentation_kwargs=kwargs,
    images_background=None,
)


# Clear explainer predict_fn as its a lambda and will be reset when loaded
explainer.predict_fn = None
with open("./mobilenet_explainer.dill", 'wb') as f:
    dill.dump(explainer, f)
