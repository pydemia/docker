#!/bin/bash

bash -c "
kubectl apply -f istio-components/expose-istio-grafana-http.yaml
kubectl apply -f istio-components/expose-istio-kiali-http.yaml
kubectl apply -f istio-components/expose-istio-prometheus-http.yaml
kubectl apply -f istio-components/expose-istio-tracing-http.yaml
" > expose-istio-components.log

bash -c "
kubectl apply -f knative-components/expose-istio-grafana-http.yaml
kubectl apply -f knative-components/expose-istio-kiali-http.yaml
kubectl apply -f knative-components/expose-istio-prometheus-http.yaml
kubectl apply -f knative-components/expose-istio-tracing-http.yaml
" > expose-knative-components.log