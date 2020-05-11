# Knative >= v0.13.0
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