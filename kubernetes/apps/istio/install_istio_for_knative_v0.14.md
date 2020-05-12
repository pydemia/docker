# Install `Istio` for `Knative`

* Prerequisite
  * `helm`


### Download `Istio`

```sh
ISTIO_VERSION=1.4.1
curl -sL https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh -
cd istio-${ISTIO_VERSION}
```

```sh
# Install CRDs
for i in install/kubernetes/helm/istio-init/files/crd*yaml; do kubectl apply -f $i; done

# Create namespace `istio-system`
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: istio-system
  labels:
    istio-injection: disabled
EOF
```

### Install `Istio`
* <font color='grey'>Installing Istio without sidecar injection</font>
* <font color='grey'>Installing Istio with sidecar injection</font>
*  **Installing Istio with SDS to secure the ingress gateway**

:bulb::speech_balloon:If you want to enable the Istio service mesh, you must enable automatic sidecar injection. The Istio service mesh provides a few benefits:

* Allows you to turn on mutual TLS, which secures service-to-service traffic within the cluster.

* Allows you to use the Istio authorization policy, controlling the access to each Knative service based on Istio service roles.

```sh
# A template with sidecar injection enabled.
helm template --namespace=istio-system \
  --set sidecarInjectorWebhook.enabled=true \
  --set sidecarInjectorWebhook.enableNamespacesByDefault=true \
  --set global.proxy.autoInject=disabled \
  --set global.disablePolicyChecks=true \
  --set prometheus.enabled=false \
  `# Disable mixer prometheus adapter to remove istio default metrics.` \
  --set mixer.adapters.prometheus.enabled=false \
  `# Disable mixer policy check, since in our template we set no policy.` \
  --set global.disablePolicyChecks=true \
  --set gateways.istio-ingressgateway.autoscaleMin=1 \
  --set gateways.istio-ingressgateway.autoscaleMax=2 \
  --set gateways.istio-ingressgateway.resources.requests.cpu=500m \
  --set gateways.istio-ingressgateway.resources.requests.memory=256Mi \
  `# Enable SDS in the gateway to allow dynamically configuring TLS of gateway.` \
  --set gateways.istio-ingressgateway.sds.enabled=true \
  `# More pilot replicas for better scale` \
  --set pilot.autoscaleMin=2 \
  `# Set pilot trace sampling to 100%` \
  --set pilot.traceSampling=100 \
  install/kubernetes/helm/istio \
  > ./istio.yaml

kubectl apply -f istio.yaml
```

### (Optional) Updating your install to use cluster local gateway
```sh
# Add the extra gateway.
helm template --namespace=istio-system \
  --set gateways.custom-gateway.autoscaleMin=1 \
  --set gateways.custom-gateway.autoscaleMax=2 \
  --set gateways.custom-gateway.cpu.targetAverageUtilization=60 \
  --set gateways.custom-gateway.labels.app='cluster-local-gateway' \
  --set gateways.custom-gateway.labels.istio='cluster-local-gateway' \
  --set gateways.custom-gateway.type='ClusterIP' \
  --set gateways.istio-ingressgateway.enabled=false \
  --set gateways.istio-egressgateway.enabled=false \
  --set gateways.istio-ilbgateway.enabled=false \
  --set global.mtls.auto=false \
  install/kubernetes/helm/istio \
  -f install/kubernetes/helm/istio/example-values/values-istio-gateways.yaml \
  | sed -e "s/custom-gateway/cluster-local-gateway/g" -e "s/customgateway/clusterlocalgateway/g" \
  > ./istio-local-gateway.yaml

kubectl apply -f istio-local-gateway.yaml
```

```sh
kubectl -n istio-system get svc istio-ingressgateway
kubectl -n istio-system get svc
```

---
### ~~(Optional) Configuring DNS~~(pending)

1. Look up the `EXTERNAL-IP` address that `Istio` received.

```sh
# $ kubectl get svc -n istio-system
# $ kubectl edit cm config-domain --namespace knative-serving


# $ kubectl -n knative-serving \
#     patch configmap config-domain --patch \
#     '{"data": {"example.com": null, "[EXTERNAL-IP].xip.io": ""}}'
# '{"data": {"example.com": null, "[CUSTOM DOMAIN]": ""}}'
# apiVersion: v1
# kind: ConfigMap
# metadata:
#   name: config-domain
#   namespace: knative-serving
# data:
#   # xip.io is a "magic" DNS provider, which resolves all DNS lookups for:
#   # *.{ip}.xip.io to {ip}.
#   34.83.80.117.xip.io: ""

```

