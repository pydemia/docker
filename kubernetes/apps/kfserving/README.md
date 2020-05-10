# KFServing

## Installation

```sh
TAG=0.2.2 && \
wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
    -O "kfserving-${TAG}.yaml"
kubectl apply -f "kfserving-${TAG}.yaml"

# TAG=v0.3.0 && \
# wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
#     -O "kfserving-${TAG}.yaml"
# kubectl apply -f "kfserving-${TAG}.yaml"
```

---

* KFServing를 서비스하는 Ingress Gateway 확인

```sh
$ kubectl -n knative-serving get cm config-istio \
  -o jsonpath="{.data['gateway\.knative-ingress-gateway']}"
istio-ingressgateway.istio-system.svc.cluster.local
```

:bell::speech_balloon:**Note**: The configuration format should be 
`gateway.{{gateway_namespace}}.{{gateway_name}}: "{{ingress_name}}.{{ingress_namespace}}.svc.cluster.local"`.
The `{{gateway_namespace}}` is optional.
when it is omitted, the system will search for the gateway in the serving system namespace `knative-serving`.
gateway.knative-serving.knative-ingress-gateway: "istio-ingressgateway.istio-system.svc.cluster.local".

* It can be shown in `ConfigMap` of `InferenceService`. It contains:
  * data
    * ingress: **Ingress** allocation info
    * logger: **Logging Pods** config
    * predictor: **Inference Container Image** info

```sh
$ kubectl -n kfserving-system get cm inferenceservice-config -o jsonpath="{.data.ingress}"
{
    "ingressGateway" : "knative-ingress-gateway.knative-serving",
    "ingressService" : "istio-ingressgateway.istio-system.svc.cluster.local"
}
```
:warning: **THIS IS _STRING_, YOU CANNOT GET `jsonpath="{.data.ingress.ingressService}"`**, only `"{.data.ingress}"`.  
*`|-` in `YAML`: multi-line string.

~~`kubectl -n kfserving-system get cm inferenceservice-config -o jsonpath="{.data.ingress}"| sed 's/^[{} \t]*//g' | awk '/"ingressService"/ {print}'`~~

---

* Get `Ingress` for `KFServing` info:
```sh
# kubectl -n istio-system get service istio-ingressgateway
# $ kubectl -n knative-serving get cm config-istio \
#     -o jsonpath="{.data['gateway\.knative-ingress-gateway']}" | cut -d '.' -f1,2 | IFS=. read ING_NM ING_NS && \
#     kubectl -n $ING_NS get service $ING_NM
$ kubectl -n knative-serving get cm config-istio \
    -o jsonpath="{.data['gateway\.knative-ingress-gateway']}" | cut -d '.' -f1,2 | IFS=. read ING_NM ING_NS && \
    kubectl -n $ING_NS get service $ING_NM
```

:no_entry: **Caution with KFServing Standalone**: 


KFServing을 독립형으로 설치했을 경우에는 KFServing 컨트롤러는 kfserving-system 네임스페이스에 배포됩니다.

KFServing은 `pod mutator`와 `mutating admission webhooks` 을 사용하여 KFServing의 스토리지 이니셜라이저(`storage initializer`) 컴포넌트를 주입합니다. 기본적으론 네임스페이스에 `control-plane` 레이블이 지정되어 있지 않으면, 해당 네임스페이스의 포드들은 `pod mutator`를 통과합니다. 그렇기 때문에 KFServing의 `pod mutator`의 `webhook`이 필요 없는 포드가 실행될때 문제가 발생할 수 있습니다.

쿠버네티스 1.14 사용자의 경우 `serving.kubeflow.org/inferenceservice: enabled` 레이블이 추가된 네임스페이스의 포드에 `ENABLE_WEBHOOK_NAMESPACE_SELECTOR` 환경변수를 추가하여, `KFServing pod mutator`를 통과하도록 하는게 좋습니다.

**Ref 1**: <https://github.com/kubeflow/kfserving#standalone-kfserving-installation>
**Ref 2**: <https://www.kangwoo.kr/2020/04/11/kubeflow-kfserving-%EC%84%A4%EC%B9%98>


```yaml
# Fro kube 1.14
env:
- name: ENABLE_WEBHOOK_NAMESPACE_SELECTOR
  value: enabled
```

```sh
# For Kube 1.15
$ kubectl patch \
    mutatingwebhookconfiguration inferenceservice.serving.kubeflow.org \
    --patch '{"webhooks":[{"name": "inferenceservice.kfserving-webhook-server.pod-mutator","objectSelector":{"matchExpressions":[{"key":"serving.kubeflow.org/inferenceservice", "operator": "Exists"}]}}]}'
mutatingwebhookconfiguration.admissionregistration.k8s.io/inferenceservice.serving.kubeflow.org patched
```

---

### Create a `VirtualService` for Health Check `istio-ingressgateway`
```bash
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: health
  namespace: knative-serving
spec:
  gateways:
  - knative-ingress-gateway
  hosts:
  - "*"
  http:
  - match:
    - headers:
        user-agent:
          prefix: GoogleHC
      method:
        exact: GET
      uri:
        exact: /
    rewrite:
      authority: istio-ingressgateway.istio-system.svc.cluster.local:15020
      uri: /healthz/ready
    route:
    - destination:
        host: istio-ingressgateway.istio-system.svc.cluster.local
        port:
          number: 15020
EOF
```

### Patch `istio-ingressgateway`: `LoadBalancer` -> `NodePort`
  * Change Service type: `LoadBalancer` -> `NodePort`
  * Annotate `cloud.google.com/neg: '{"ingress": true}'`

```json
cat <<EOF > istio-ingressgateway-patch.json
[
  {
    "op": "replace",
    "path": "/spec/type",
    "value": "NodePort"
  },
  {
    "op": "remove",
    "path": "/status"
  },
  {
    "op": "remove",
    "path": "/metadata/annotations/addonmanager.kubernetes.io/mode=Reconcile`"}
  },
]
EOF
kubectl -n istio-system patch svc istio-ingressgateway \
  --type=json -p="$(cat istio-ingressgateway-patch.json)"
```

:bulb: This changes existing `istio-ingressgateway` as the following:

  * Annotate `cloud.google.com/neg: '{"ingress": true}'`.
    This Creates [Ref.](https://cloud.google.com/kubernetes-engine/docs/how-to/container-native-load-balancing#create_service)
```sh
kubectl annotate svc istio-ingress -n istio-system cloud.google.com/neg='{"exposed_ports": {"80":{}}}'
```
Annotations
`addonmanager.kubernetes.io/mode=Reconcile`
`kubernetes.io/cluster-service : true` -> will be deprecated
<https://github.com/kubernetes/kubernetes/blob/master/cluster/addons/addon-manager/README.md>


#### ~~Serve Multiple Apps on ONE LoadBalancer~~

```yaml
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1beta1
# Ingress
kind: Ingress
metadata:
  name: kfserving-ingress
  namespace: istio-system
  annotations:
spec:
  rules:
  - http:
      paths:
      - path: /*
        backend:
          serviceName: istio-ingressgateway
          servicePort: 80
EOF
```

---

## 5. Set `inferenceservice`

```bash
# kubectl apply -f examples/sklearn/sklearn.yaml
$ curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/sklearn.yaml -O && \
  kubectl apply -f sklearn.yaml

inferenceservice.serving.kubeflow.org/sklearn-iris created
```

> :no_entry: **Error Case:**
> ```ascii
> Error from server (InternalError): error when creating "sklearn.yaml": Internal error occurred: > failed calling webhook "inferenceservice.kfserving-webhook-server.defaulter": Post https://> kfserving-webhook-server-service.kfserving-system.svc:443/mutate-inferenceservices?timeout=30s: > net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting > headers)
> ```
> 
> :white_check_mark:**Troubleshooting:**
> 
> ```sh
> $ kubectl get po -n kfserving-system
> 
> 
> # If it is, more often than not, it is caused by a stale webhook, since webhooks are immutable.
> # Even if the KFServing controller is not running,
> # you might have stale webhooks from last deployment causing other issues.
> # Best is to delete them, and test again
> $ kubectl -n kfserving-system \
>       delete mutatingwebhookconfigurations inferenceservice.serving.kubeflow.org && \
>     kubectl delete validatingwebhookconfigurations inferenceservice.serving.kubeflow.org && \
>     kubectl delete po kfserving-controller-manager-0
> mutatingwebhookconfiguration.admissionregistration.k8s.io "inferenceservice.serving.kubeflow.org" deleted
> validatingwebhookconfiguration.admissionregistration.k8s.io "inferenceservice.serving.kubeflow.> org" deleted
> pod "kfserving-controller-manager-0" deleted
> ```

---
## 5. Set `inferenceservice`

```bash
$ curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/iris-input.json -O && \
  kubectl apply -f sklearn.yaml  
inferenceservice.serving.kubeflow.org/sklearn-iris created
```

## 6. Get a prediction

```bash
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/iris-input.json -O

MODEL_NAME=sklearn-iris
INPUT_PATH=@./iris-input.json
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

CLUSTER_IP=$(kubectl -n istio-system get ing kfserving-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')


sleep 20s

SERVICE_HOSTNAME=$(kubectl get inferenceservice sklearn-iris -o jsonpath='{.status.url}' | cut -d "/" -f 3)

curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```

```bash
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/iris-input.json -O

MODEL_NAME=sklearn-iris
INPUT_PATH=@./iris-input.json
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

CLUSTER_IP=$(kubectl -n istio-system get ing kfserving-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')


SERVICE_HOSTNAME=$(kubectl get inferenceservice sklearn-iris -o jsonpath='{.status.url}' | cut -d "/" -f 3)

curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```

---

### Volume

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: kfserving-models-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

---
