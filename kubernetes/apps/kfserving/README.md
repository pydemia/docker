# KFServing

## Installation

```sh
TAG=0.2.2 && \
wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
    -O "kfserving-${TAG}.yaml"
kubectl apply -f "kfserving-${TAG}.yaml"

TAG=v0.3.0 && \
wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
    -O "kfserving-${TAG}.yaml"
kubectl apply -f "kfserving-${TAG}.yaml"
```


## `kfserving-ingress`

Sidecar Injection:
1. <https://cloud.google.com/istio/docs/istio-on-gke/installing#enabling_sidecar_injection>
2. https://istio.io/docs/setup/additional-setup/sidecar-injection/

`kfserving-ingress.yaml`:
```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: kfserving-ingress
  namespace: kfserving-system
spec:
  backend:
    serviceName: istio-ingress
    servicePort: 80
```


```sh
$ kubectl apply -f kfserving-ingress.yaml
ingress.extensions/kfserving-ingress created

$ kubectl get ingress kfserving-ingress -n kfserving-system --watch
$ INGRESS_IP=$(kubectl get ingress kfserving-ingress \
   -n kfserving-system \
    --output jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

---

Refer to [this](https://cloud.google.com/solutions/integrating-https-load-balancing-with-istio-and-cloud-run-for-anthos-deployed-on-gke)

* Creating a GKE cluster
> `addons Istio` and install `Knative` manually :That is not working.
> Install CloudRun to Bypass the error
```sh
CLUSTER_NM=kfserving-sklearn-test
ZONE=us-central1-f
gcloud beta container clusters create $CLUSTER_NM \
    --addons HorizontalPodAutoscaling,HttpLoadBalancing,Istio,CloudRun \
    --istio-config=auth=MTLS_PERMISSIVE \
    --cluster-version=1.15.9-gke.24 \
    --enable-ip-alias \
    --enable-stackdriver-kubernetes \
    --machine-type n1-standard-2 \
    --zone $ZONE \
    --no-enable-autoupgrade \
    --metadata disable-legacy-endpoints=true
```

Show the `current-context`:
```sh
$ kubectl config current-context
gke_ds-ai-platform_us-central1-f_kfserving-sklearn-test
```

or select it:

```sh
$ gcloud container clusters get-credentials $CLUSTER_NM \
  --region $ZONE
  #--project ds-ai-platform
```

* ~~Install `Knative`: [ref](https://knative.dev/v0.11-docs/install/knative-with-gke/)~~

```sh
kubectl apply --selector knative.dev/crd-install=true \
--filename https://github.com/knative/serving/releases/download/v0.11.0/serving.yaml \
--filename https://github.com/knative/eventing/releases/download/v0.11.0/release.yaml \
--filename https://github.com/knative/serving/releases/download/v0.11.0/monitoring.yaml && \
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.11.0/serving.yaml \
--filename https://github.com/knative/eventing/releases/download/v0.11.0/release.yaml \
--filename https://github.com/knative/serving/releases/download/v0.11.0/monitoring.yaml
```
[**NOTE**](https://redhat-developer-demos.github.io/knative-tutorial/knative-tutorial-basics/0.7.x/01-setup.html): First time when you run the above command will show some warnings and error as shown below, **you can either safely ignore them or re-running the above command will cause the errors to disappear.**

```ascii
unable to recognize "https://github.com/knative/serving/releases/download/v0.7.1/serving.yaml": no matches for kind "Image" in version "caching.internal.knative.dev/v1alpha1"
unable to recognize "https://github.com/knative/eventing/releases/download/v0.7.1/release.yaml": no matches for kind "ClusterChannelProvisioner" in version "eventing.knative.dev/v1alpha1"

```


* Handling health check requests
```sh
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: health
  namespace: knative-serving
spec:
  gateways:
  - gke-system-gateway
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
      authority: istio-ingress.gke-system.svc.cluster.local:15020
      uri: /healthz/ready
    route:
    - destination:
        host: istio-ingress.gke-system.svc.cluster.local
        port:
          number: 15020
EOF
```

* Modifying the Istio ingress gateway for use with Kubernetes Ingress

1. Create a JSON Patch file to make changes to the Istio ingress gateway:
```sh
cat <<EOF > istio-ingress-patch.json
[
  {
    "op": "replace",
    "path": "/spec/type",
    "value": "NodePort"
  },
  {
    "op": "remove",
    "path": "/status"
  }
]
EOF
```

2. Apply the patch file and add the Istio ingress gateway as a backend:
```sh
kubectl -n gke-system patch svc istio-ingress \
    --type=json -p="$(cat istio-ingress-patch.json)" \
    --dry-run=true -o yaml | kubectl apply -f -
kubectl annotate svc istio-ingress -n gke-system cloud.google.com/neg='{"exposed_ports": {"80":{}}}'
```

This patch makes the following changes to the Kubernetes Service object of the Istio ingress gateway:

* Adds the annotation cloud.google.com/neg: '{"ingress": true}'. This annotation creates a network endpoint group and enables container-native load balancing when the Kubernetes Ingress object is created.
* Changes the Kubernetes Service type from LoadBalancer to NodePort. This change removes the Network Load Balancing resources.

