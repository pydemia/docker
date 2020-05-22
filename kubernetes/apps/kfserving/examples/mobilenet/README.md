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
        image_bytes = base64.b64decode(b64_byte_string)
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

```sh
$ cd predictor/mobilenet_saved_model
$ saved_model_cli show --dir . --tag_set serve --signature_def serving_default                                                                                                      [Fri 05/22 2020 11:35:51 KST]
2020-05-22 11:35:53.789841: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libnvinfer.so.6'; dlerror: libnvinfer.so.6: cannot open shared object file: No such file or directory; LD_LIBRARY_PATH: /usr/local/cuda-10.0/include:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/include:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/include:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/include:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64
2020-05-22 11:35:53.789898: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libnvinfer_plugin.so.6'; dlerror: libnvinfer_plugin.so.6: cannot open shared object file: No such file or directory; LD_LIBRARY_PATH: /usr/local/cuda-10.0/include:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/include:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/include:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/include:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64
2020-05-22 11:35:53.789907: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:30] Cannot dlopen some TensorRT libraries. If you would like to use Nvidia GPU with TensorRT, please make sure the missing libraries mentioned above are installed properly.
The given SavedModel SignatureDef contains the following input(s):
  inputs['input_1'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 224, 224, 3)
      name: serving_default_input_1:0
The given SavedModel SignatureDef contains the following output(s):
  outputs['act_softmax'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 1000)
      name: StatefulPartitionedCall:0
Method name is: tensorflow/serving/predict
```

## Create a transformer for pre-processing and post-processing


```sh
# cd mobilenet
docker build -t pydemia/mobilenet_transformer:latest -f transformer.Dockerfile .

TRANSFORMER_VERSION="tf1.15.2-0.1.1"
docker tag \
    pydemia/mobilenet_transformer:latest \
    pydemia/mobilenet_transformer:$TRANSFORMER_VERSION

docker tag \
    pydemia/mobilenet_transformer:$TRANSFORMER_VERSION \
    gcr.io/ds-ai-platform/mobilenet_transformer:$TRANSFORMER_VERSION

docker push \
    gcr.io/ds-ai-platform/mobilenet_transformer:$TRANSFORMER_VERSION
docker push \
    pydemia/mobilenet_transformer:$TRANSFORMER_VERSION

```


```sh
# cd mobilenet

# Predictor: tensorflow/serving:1.15.2
gsutil -m cp -r ./predictor/mobilenet_saved_model gs://yjkim-models/kfserving/mobilenet/predictor/

# Transformer: custom container
docker push gcr.io/ds-ai-platform/mobilenet_transformer:$TRANSFORMER_VERSION

# Exaplainer: alibi: type:AnchorImages
gsutil -m cp -r ./explainer/explainer.dill gs://yjkim-models/kfserving/mobilenet/explainer/
```

```sh
# cd mobilenet

# Predictor: tensorflow/serving:1.15.2
aws s3 cp --recursive ./predictor/mobilenet_saved_model s3://yjkim-models/kfserving/mobilenet/predictor/mobilenet_saved_model

# Transformer: custom container
docker push docker.io/pydemia/mobilenet_transformer:$TRANSFORMER_VERSION

# Exaplainer: alibi: type:AnchorImages
aws s3 cp --recursive ./explainer s3://yjkim-models/kfserving/mobilenet/explainer
```

```sh
python -m mobilenet_image_loader -i ./elephant.jpg -o ./input.json -ot b64


INFERENCE_NS="default"

# MODEL_NAME="mobilenet"
MODEL_NAME="mobilenet-trn"  # mobilenet, transformer
# MODEL_NAME="mobilenet-exp"  # mobilenet, explainer
# MODEL_NAME="mobilenet-fullstack"  # mobilenet, transformer, explainer

#INPUT_PATH="@./elephant.json"
INPUT_PATH="@./input.json"

# APPLY
# kubectl -n $INFERENCE_NS apply -f mobilenet-fullstack.yaml

kubectl -n $INFERENCE_NS wait --for=condition=ready inferenceservice $MODEL_NAME
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "$CLUSTER_IP, $SERVICE_HOSTNAME"

# PREDICTION
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH

 
```
:warning:
```sh
{ "error": "Failed to process element: 0 key: image_bytes of \'instances\' list. Error: Invalid argument: JSON object: does not have named input: image_bytes" }%   
```

```sh
$ saved_model_cli show --dir . --tag_set serve --signature_def serving_default

The given SavedModel SignatureDef contains the following input(s):
  inputs['input_1'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 224, 224, 3)
      name: serving_default_input_1:0
The given SavedModel SignatureDef contains the following output(s):
  outputs['act_softmax'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 1000)
      name: StatefulPartitionedCall:0
Method name is: tensorflow/serving/predict
```

:warning:
```sh
DWTcja49DWvN1rJuvvGgZl34zAmezGs8NtYEdjWhf/AOpH1/xrPHU1jLcpHbW0omtY3B4YCkccFT0NVNGJOmLn3q3J0rZbEmbJmOQoenUVLBJztqO+6p9aZGTvBpAaQ+YfSoJUzk1Knf6UjfcNUBiXSFTVHcUc+hrTvvu/hWY4+UVEhkoIYUx0psR+apm6VBRUZcUYFSuKZgUAf//Z\" Type: String is not of expected type: float" }
```

