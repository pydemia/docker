# KF Serving with creating an inference cluster

## 1. Create a cluster, which has `HTTP LoadBalancer`, `Istio`, `Knative`

**Info**: `addons Istio` and install `Knative` manually:It is not working.
Install `CloudRun` to bypass the problem

<https://cloud.google.com/kubernetes-engine/docs/concepts/private-cluster-concept#overview>
```bash
CLUSTER_NM=kfserving-sklearn1
ZONE=us-central1-f
gcloud beta container clusters create $CLUSTER_NM \
    --addons HorizontalPodAutoscaling,HttpLoadBalancing,Istio,CloudRun \
    --istio-config=auth=MTLS_PERMISSIVE \
    --cluster-version=1.15.9-gke.24 \
    --enable-stackdriver-kubernetes \
    --machine-type n1-standard-2 \
    --zone $ZONE \
    --no-enable-autoupgrade \
    --metadata disable-legacy-endpoints=true \
    --enable-ip-alias \
    --enable-private-nodes \
    --no-enable-master-authorized-networks \
    --master-ipv4-cidr 172.16.0.0/28
```

Show the `current-context`:
```bash
kubectl config current-context
```

or select it:

```bash
gcloud container clusters get-credentials $CLUSTER_NM \
  --region $ZONE
  #--project ds-ai-platform
```

Result:
![](after_cluster_creation.png)

## 4. Install `KFServing`

```bash
TAG=0.2.2 && \
wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
    -O "kfserving-${TAG}.yaml"
kubectl apply -f "kfserving-${TAG}.yaml"
```

## 5. Set `inferenceservice`

```bash
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/sklearn.yaml -O
kubectl apply -f sklearn.yaml
```

## 6. Get a prediction

```bash
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/iris-input.json -O

MODEL_NAME=sklearn-iris
INPUT_PATH=@./iris-input.json
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
sleep 20s
SERVICE_HOSTNAME=$(kubectl get inferenceservice sklearn-iris -o jsonpath='{.status.url}' | cut -d "/" -f 3)
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```

Then, the output would be the following:
```ascii
* Expire in 0 ms for 6 (transfer 0x56322055d560)
*   Trying 104.154.142.146...
* TCP_NODELAY set
* Expire in 200 ms for 4 (transfer 0x56322055d560)
* Connected to 104.154.142.146 (104.154.142.146) port 80 (#0)
> POST /v1/models/sklearn-iris:predict HTTP/1.1
> Host: sklearn-iris.default.example.com
> User-Agent: curl/7.64.0
> Accept: */*
> Content-Length: 76
> Content-Type: application/x-www-form-urlencoded
>
* upload completely sent off: 76 out of 76 bytes
< HTTP/1.1 200 OK
< content-length: 23
< content-type: text/html; charset=UTF-8
< date: Thu, 07 May 2020 18:19:23 GMT
< server: istio-envoy
< x-envoy-upstream-service-time: 8105
<
* Connection #0 to host 104.154.142.146 left intact
{"predictions": [1, 1]}%
```

Done.

---

## 3-2, 3-3. Add Other port to `ingressgateway`

* HTTP
```bash
kubectl apply -f - <<EOF
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: my-ingress-http
  namespace: gke-system
spec:
  backend:
    serviceName: istio-ingress
    servicePort: 80
EOF
```
spec:
  clusterIP: 10.3.15.10
  externalTrafficPolicy: Cluster
  ports:
  - name: status-port
    nodePort: 31017
    port: 15020
    protocol: TCP
    targetPort: 15020
  - name: http2
    nodePort: 32195
    port: 80
    protocol: TCP
    targetPort: 80
  - name: https
    nodePort: 30050
    port: 443
    protocol: TCP
    targetPort: 443
**Tip**: Using `kubectl patch` and `{"op": "add"}`
```sh
kubectl patch svc istio-ingress --type='json' \
-p='
[
  {
    "op": "add",
    "path": "/spec/ports",
    "value": {
      "name": "custom-port",
      "nodePort": "",
      "port": "",
      "protocol": "TCP",
      "targetPort": ""
    }
  }
]
'

kubectl patch svc istio-ingressgateway --type='json' \
-p='
[
  {
    "op": "add",
    "path": "/spec/ports",
    "value": {
      "name": "custom-port",
      "nodePort": "",
      "port": "",
      "protocol": "TCP",
      "targetPort": ""
    }
  }
]
'

```

Next Step: **Using `sidecar injection` with `Istio`**

Further Readings about **Sidecar Injection**
1. <https://cloud.google.com/istio/docs/istio-on-gke/installing#enabling_sidecar_injection>
2. https://istio.io/docs/setup/additional-setup/sidecar-injection/

Prerequisite: [`istioctl`](../../istio/README.md#install-istioctl)