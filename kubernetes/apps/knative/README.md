
`Knative == v0.12`: https://knative.dev/v0.12-docs/install/knative-with-gke/
`Knative == v0.14`: https://knative.dev/docs/install/any-kubernetes-cluster/


| ![](knative-arch.png) |
| ----- |
Installing cluster-local-gateway for serving cluster-internal traffic
If you installed Istio, you can install a cluster-local-gateway within your Knative cluster so that you can serve cluster-internal traffic. If you want to configure your revisions to use routes that are visible only within your cluster, install and use the cluster-local-gateway

1. Install the `CRDs(Custom Resource Definitions)`
2. Install the core components of `Serving`

## Knative >= v0.13.0

```sh
DIR=knative-v0.13.0
mkdir -p $DIR;cd $DIR

# 1. Install the `CRDs(Custom Resource Definitions)`
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/serving-crds.yaml -O && \
    kubectl apply -f serving-crds.yaml
# 2. Install the core components of `Serving`
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/serving-core.yaml -O && \
    kubectl apply -f serving-core.yaml
# 3-1. Install the Knative Istio controller:
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/serving-istio.yaml -O && \
    kubectl apply -f serving-istio.yaml
# 4. Configure DNS: Magic DNS (`xip.io`)
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/serving-default-domain.yaml -O && \
    kubectl apply -f serving-default-domain.yaml
# 5. Monitor all Knative components are running:
kubectl get pods --namespace knative-serving
# 6. Optional Serving extensions
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/serving-hpa.yaml -O && \
    kubectl apply -f serving-hpa.yaml
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/serving-cert-manager.yaml -O && \
    kubectl apply -f serving-cert-manager.yaml
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/serving-nscert.yaml -O && \
    kubectl apply -f serving-nscert.yaml
# 7. Eventing Components
curl -sL https://github.com/knative/eventing/releases/download/v0.13.0/eventing-crds.yaml -O && \
    kubectl apply -f eventing-crds.yaml
curl -sL https://github.com/knative/eventing/releases/download/v0.13.0/eventing-core.yaml -O && \
    kubectl apply -f eventing-core.yaml
# GCP Pub/Sub Case
curl -sL https://github.com/google/knative-gcp/releases/download/v0.13.0/cloud-run-events.yaml -O && \
    kubectl apply -f cloud-run-events.yaml
curl -sL https://github.com/knative/eventing/releases/download/v0.13.0/channel-broker.yaml -O && \
    kubectl apply -f channel-broker.yaml
# 8. Observability Plugins
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/monitoring-core.yaml -O && \
    kubectl apply -f monitoring-core.yaml
curl -sL https://github.com/knative/serving/releases/download/v0.13.0/monitoring-metrics-prometheus.yaml -O && \
    kubectl apply -f monitoring-metrics-prometheus.yaml

cd ..
```

### Serving Components
```sh
# 1. Install the `CRDs(Custom Resource Definitions)`
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/serving-crds.yaml
# 2. Install the core components of `Serving`
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/serving-core.yaml
```

#### Pick a networking layer (`Istio`)
```sh
# 3-1. Install the Knative Istio controller:
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/serving-istio.yaml
# 3-2. Fetch the External IP or CNAME:
kubectl --namespace istio-system get service istio-ingressgateway
# Save this for configuring DNS below.
```

#### 4. Configure DNS: Magic DNS (`xip.io`)

We ship a simple Kubernetes Job called “default domain” that will (see caveats) configure Knative Serving to use xip.io as the default DNS suffix.

**Caveat**: This will only work if the cluster LoadBalancer service exposes an IPv4 address, so it will not work with IPv6 clusters, AWS, or local setups like Minikube. For these, see “Real DNS”.
```sh
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/serving-default-domain.yaml
```

#### 5. Monitor all Knative components are running:
```sh
kubectl get pods --namespace knative-serving
```

#### 6. Optional Serving extensions
##### 6-1. TLS with cert-manager
```sh
# Knative supports automatically provisioning TLS certificates via cert-manager.
# The following commands will install the components needed to support the
# provisioning of TLS certificates via cert-manager.

# 6-1-1. Install `cert-manager 0.12.0 and higher

# 6-1-2 Install the component that integrates Knative with cert-manager:
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/serving-hpa.yaml
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/serving-cert-manager.yaml
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/serving-nscert.yaml
```

### 7. Eventing Components

```sh
kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.13.0/eventing-crds.yaml
kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.13.0/eventing-core.yaml
# GCP Pub/Sub Case
kubectl apply --filename https://github.com/google/knative-gcp/releases/download/v0.13.0/cloud-run-events.yaml
kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.13.0/channel-broker.yaml
```

---

### 8. Observability Plugins

#### Install Core

```sh
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/monitoring-core.yaml
```

#### Plugins for Prometheus and Grafana

```sh
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/monitoring-metrics-prometheus.yaml
```

#### Plugins for ELK stack

```sh
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/monitoring-logs-elasticsearch.yaml
```

#### Plugins for Jaeger(Standalone)

```sh
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/monitoring-tracing-jaeger-in-mem.yaml
```

#### Plugins for Zipkin(Standalone)

```sh
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/monitoring-tracing-zipkin-in-mem.yaml
```





---

## Knative <= v0.12.0
```sh
# 1. Install the `CRDs(Custom Resource Definitions)`
$ kubectl apply --selector knative.dev/crd-install=true \
    --filename https://github.com/knative/serving/releases/download/v0.12.0/serving.yaml \
    --filename https://github.com/knative/eventing/releases/download/v0.12.0/eventing.yaml \
    --filename https://github.com/knative/serving/releases/download/v0.12.0/monitoring.yaml

# 2. Install the core components of `Serving`
$ kubectl apply --filename https://github.com/knative/serving/releases/download/v0.12.0/serving.yaml \
    --filename https://github.com/knative/eventing/releases/download/v0.12.0/eventing.yaml \
    --filename https://github.com/knative/serving/releases/download/v0.12.0/monitoring.yaml

# 3. Monitor all Knative components are running:
$ kubectl get pods --namespace knative-serving
$ kubectl get pods --namespace knative-eventing
$ kubectl get pods --namespace knative-monitoring
```