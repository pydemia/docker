# KFServing with MobileNet

* `transformer-preprocessing`
* `predictor`
* `transformer-postprocessing`
* `explainer`

---

## Full workflow

```py
import tensorflow as tf
print('tensorflow: ', tf.__version__)

mobnet = tf.keras.applications.mobilenet
pre_processing_fn = mobnet.preprocess_input
post_processing_fn = mobnet.decode_predictions

model = mobnet.MobileNet(weights='imagenet')
model.save('./mobilenet_saved_model', save_format='tf')

image_saved_path = tf.keras.utils.get_file(
    "grace_hopper.jpg",
    "https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg",
)


# Preprocessing -----------------------------
def _load_b64_string_to_img(b64_byte_string):
        image_bytes = base64.b64decode(image_byte_string)
        image_data = BytesIO(image_bytes)
        img = Image.open(image_data)
        return img

def preprocess_fn(instance):
    img = _load_b64_string_to_img(instance['image_bytes'])
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    # The inputs pixel values are scaled between -1 and 1, sample-wise.
    x = tf.keras.applications.mobilenet.preprocess_input(
        img_array,
        data_format='channels_last',
    )
    x = np.expand_dims(x, axis=0)
    return x


# Load a model ------------------------------
model = tf.saved_model.load('./mobilenet_saved_model')


# Postprocessing ----------------------------
def postprocess_fn(pred):
    decoded = tf.keras.applications.mobilenet.decode_predictions(
        [pred], top=5
    )
    return decoded


```

## Get `Saved_Model` for predictor

`get_saved_model.py`
```py
import tensorflow as tf
print('tensorflow: ', tf.__version__)

mobnet = tf.keras.applications.mobilenet

model = mobnet.MobileNet(weights='imagenet')
model.save('./mobilenet_saved_model', save_format='tf')
preprocessing = mobnet.preprocess_input
post_processing = mobnet.decode_predictions
```

## Create a transformer for pre-processing and post-processing


```sh
docker build -t pydemia/mobilenet_transformer:latest -f transformer.Dockerfile .
docker tag pydemia/mobilenet_transformer:latest gcr.io/ds-ai-platform/mobilenet_transformer:latest
# docker push gcr.io/ds-ai-platform/mobilenet_transformer:latest
```


```sh
# Predictor: tensorflow/serving:1.15
gsutil -m cp -r ./predictor/mobilenet_saved_model gs://yjkim-models/kfserving/mobilenet/predictor/

# Transformer: custom container
docker push docker push gcr.io/ds-ai-platform/mobilenet_transformer:latest

# Exaplainer: alibi: type:AnchorImages
gsutil -m cp -r ./explainer/mobilenet_explainer.dill gs://yjkim-models/kfserving/mobilenet/explainer/
```



```py
# i = tf.keras.layers.Input([None, None, 3], dtype = tf.uint8)
# x = tf.cast(i, tf.float32)
# x = tf.keras.applications.mobilenet.preprocess_input(x, data_format=None)

# result = tf.keras.applications.mobilenet.decode_predictions(
#     preds, top=5
# )


# nohup tensorflow_model_server \
#   --rest_api_port=8501 \
#   --model_name=mobilenet \
#   --model_base_path="/tmp/mobilenet" >server.log 2>&1


# !pip install -q requests
# import json
# import numpy
# import requests
# data = json.dumps({"signature_name": "serving_default",
#                    "instances": x.tolist()})
# headers = {"content-type": "application/json"}
# json_response = requests.post('http://localhost:8501/v1/models/mobilenet:predict',
#                               data=data, headers=headers)
# predictions = numpy.array(json.loads(json_response.text)["predictions"])
```