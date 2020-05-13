#!/bin/bash

# Knative >= v0.14.0
KNATIVE_VERSION="v0.14.0"
DIR="knative-${KNATIVE_VERSION}"
PWD_START="$(pwd)"
mkdir -p $DIR;cd $DIR

# 1. Install the `CRDs(Custom Resource Definitions)`
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-crds.yaml -O && \
    kubectl apply -f serving-crds.yaml
# 2. Install the core components of `Serving`
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-core.yaml -O && \
    kubectl apply -f serving-core.yaml

sleep 20
# 3-1. Install the Knative Istio controller:
curl -sL https://github.com/knative/net-istio/releases/download/${KNATIVE_VERSION}/release.yaml -o serving-istio.yaml && \
    kubectl apply --filename serving-istio.yaml

curl -sL https://github.com/knative/net-istio/releases/download/${KNATIVE_VERSION}/net-istio.yaml -O && \
    kubectl apply --filename net-istio.yaml

# v0.13.0[NAME CHANGED]
# curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-istio.yaml -O && \
#     kubectl apply -f serving-istio.yaml

kubectl --namespace istio-system get service istio-ingressgateway
# # 4. Configure DNS: Magic DNS (`xip.io`)
# curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-default-domain.yaml -O && \
#     kubectl apply -f serving-default-domain.yaml
# 4. Real DNS
# 4-A. If the networking layer produced an External IP address,
# then configure a wildcard A record for the domain:
# (Here knative.example.com is the domain suffix for your cluster)
# *.knative.example.com == A 35.233.41.212
# 4-B. If the networking layer produced a CNAME,
# then configure a CNAME record for the domain:
# *.knative.example.com == CNAME a317a278525d111e89f272a164fd35fb-1510370581.eu-central-1.elb.amazonaws.com

# # Replace knative.example.com with your domain suffix
# kubectl patch configmap/config-domain \
#   --namespace knative-serving \
#   --type merge \
#   --patch '{"data":{"knative.example.com":""}}'

# 5. Monitor all Knative components are running:
kubectl get pods --namespace knative-serving

# 6. Optional Serving extensions
# HPA autoscaling(Horizontal Pod Autoscaler)
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-hpa.yaml -O && \
    kubectl apply -f serving-hpa.yaml
# TLS cert-manager
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-cert-manager.yaml -O && \
    kubectl apply -f serving-cert-manager.yaml
# TLS via HTTP01
curl https://github.com/knative/net-http01/releases/download/${KNATIVE_VERSION}/release.yaml 0 serving-http01.yaml && \
    kubectl apply --filename serving-http01.yaml
# TLS wildcard
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-nscert.yaml -O && \
    kubectl apply -f serving-nscert.yaml

# 7. Eventing Components
curl -sL https://github.com/knative/eventing/releases/download/${KNATIVE_VERSION}/eventing-crds.yaml -O && \
    kubectl apply -f eventing-crds.yaml
curl -sL https://github.com/knative/eventing/releases/download/${KNATIVE_VERSION}/eventing-core.yaml -O && \
    kubectl apply -f eventing-core.yaml

# Kafka Case
curl -sL https://github.com/knative/eventing-contrib/releases/download/${KNATIVE_VERSION}/kafka-source.yaml -O && \
    kubectl apply -f kafka-source.yaml

# # GCP Pub/Sub Case
# curl -sL https://github.com/google/knative-gcp/releases/download/${KNATIVE_VERSION}/cloud-run-events.yaml -O && \
#     kubectl apply -f cloud-run-events.yaml
# curl -sL https://github.com/knative/eventing/releases/download/${KNATIVE_VERSION}/channel-broker.yaml -O && \
#     kubectl apply -f channel-broker.yaml

# 8. Observability Plugins
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/monitoring-core.yaml -O && \
    kubectl apply -f monitoring-core.yaml
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/monitoring-metrics-prometheus.yaml -O && \
    kubectl apply -f monitoring-metrics-prometheus.yaml

cd $PWD_START