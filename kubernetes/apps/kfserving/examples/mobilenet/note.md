```bash
docker run --rm -it -p 8080:80 gcr.io/kfserving/alibi-explainer:v0.3.0 \
    --http_port 80 \
    --workers 1 \
    --storage_uri s3://yjkim-models/kfserving/mobilenet/explainer \
    --model_name mobilenet-fullstack \
    --predictor_host http://35.223.25.173/v1/models/mobilenet-fullstack

```

```sh

INFERENCE_NS="default"
MODEL_NAME="mobilenet-fullstack"
INPUT_PATH="@./input.json"

kubectl -n $INFERENCE_NS wait --for=condition=ready --timeout=90s\
    inferenceservice $MODEL_NAME
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "$CLUSTER_IP, $SERVICE_HOSTNAME"

curl -v -H "Host: ${SERVICE_HOSTNAME}" http://35.223.25.173/v1/models/mobilenet-fullstack:explain -d @./input.json > ./output_explain.json


# PREDICTION
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH > ./output.json

# EXPLANATION
# curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:explain -d $INPUT_PATH > ./output_explain.json

curl -v -H "Host: ${SERVICE_HOSTNAME}" http://35.223.25.173/v1/models/mobilenet-fullstack:explain -d @./input.json > ./output_explain.json


# Get Logs
kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=explainer -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container


kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=transformer -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container


kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=predictor -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container


kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=transformer -o jsonpath='{.items[0].metadata.name}')" -c queue-proxy


python json_image_parser.py -i output.json -o output_result 
```


```sh

INFERENCE_NS="default"
MODEL_NAME="mobilenet-exp"  # mobilenet, explainer
INPUT_PATH="@./input.json"

# kubectl -n $INFERENCE_NS apply -f mobilenet-explainer.yaml
# kubectl -n $INFERENCE_NS delete -f mobilenet-explainer.yaml

kubectl -n $INFERENCE_NS wait --for=condition=ready --timeout=90s\
    inferenceservice $MODEL_NAME
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "$CLUSTER_IP, $SERVICE_HOSTNAME"


curl -v -H "Host: ${SERVICE_HOSTNAME}" http://35.223.25.173/v1/models/mobilenet-exp:explain -d @./input.json > ./output_explain.json


python test_explainer.py \
    --cluster_ip $CLUSTER_IP \
    --hostname $SERVICE_HOSTNAME \
    --op predict

python test_explainer.py \
    --cluster_ip $CLUSTER_IP \
    --hostname $SERVICE_HOSTNAME \
    --op explain

```