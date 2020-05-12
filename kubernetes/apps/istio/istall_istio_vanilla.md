# Istio


## Download `Istio`

```sh
curl -sL https://istio.io/downloadIstio | ISTIO_VERSION=1.4.1 sh -
```


## Install `Istio`

```sh
cd istio-1.4.1 && \
  istioctl manifest apply \
  --set values.global.mtls.enabled=true

# istioctl manifest apply
# --set values.global.controlPlaneSecurityEnabled=true

# istio 1.5
# istioctl manifest apply --set addonComponents.grafana.enabled=true
```

In case `istio-injection=enabled` on namespace `default`:
```sh
kubectl label namespace default istio-injection=enabled
```
