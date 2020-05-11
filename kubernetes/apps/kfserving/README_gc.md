
---

### Create a `VirtualService` for Health Check `istio-ingress`

| Cluster version | `ISTIO-GATEWAY` | `NAMESPACE` |
| :--- | :-- | :-- |
| `1.15.3-gke.19` and greater<br>`1.14.3-gke.12` and greater<br>`1.13.10-gke.8` and greater	| `istio-ingress` |`gke-system` |
| All other versions | `istio-ingressgateway` | `istio-system` |

:star::warning:**Note**: 
For cluster versions `1.15.3-gke.19` and greater, `1.14.3-gke.12` and greater, and `1.13.10-gke.8` and greater,   **`istio-ingress` is the Kubernetes service created by `Istio` as the shared gateway for all traffic incoming to the cluster.**
For all other cluster versions, `istio-ingressgateway` is the service for this.

<https://cloud.google.com/run/docs/gke/troubleshooting#ip-pending>

```bash
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

### Patch `istio-ingressgateway`: `LoadBalancer` -> `NodePort`
  * Change Service type: `LoadBalancer` -> `NodePort`
  * Annotate `cloud.google.com/neg: '{"ingress": true}'`

```json
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
kubectl -n gke-system patch svc istio-ingress \
    --type=json -p="$(cat istio-ingress-patch.json)" \
    --dry-run=true -o yaml | kubectl apply -f -
kubectl annotate svc istio-ingress -n gke-system cloud.google.com/neg='{"exposed_ports": {"80":{}}}'
```

:bulb: This changes existing `istio-ingress` as the following:

  * Annotate `cloud.google.com/neg: '{"ingress": true}'`.
    This Creates [Ref.](https://cloud.google.com/kubernetes-engine/docs/how-to/container-native-load-balancing#create_service)
```sh
# kubectl annotate svc istio-ingress -n istio-system cloud.google.com/neg='{"exposed_ports": {"80":{}}}'
# kubectl annotate svc -n istio-system istio-ingressgateway cloud.google.com/neg='{"ingress": true}'
```
Annotations
`addonmanager.kubernetes.io/mode=Reconcile`
`kubernetes.io/cluster-service : true` -> will be deprecated
<https://github.com/kubernetes/kubernetes/blob/master/cluster/addons/addon-manager/README.md>


#### ~~Serve Multiple Apps on ONE LoadBalancer~~

```yaml
kubectl apply -f - <<EOF
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: kfserving-ingress
  namespace: gke-system
spec:
  backend:
    serviceName: istio-ingress
    servicePort: 80
EOF
```

```yaml
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1beta1
# Ingress
kind: Ingress
metadata:
  name: kfserving-ingress
  namespace: gke-system
  annotations:
spec:
  rules:
  - http:
      paths:
      - path: /*
        backend:
          serviceName: istio-ingress
          servicePort: 80
EOF
```