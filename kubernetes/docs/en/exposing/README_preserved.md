
###### 2-3. In GCP, use GKE Provided Health Check

Prerequisite: `Knative-serving`, `Istio` and `GKE`

* Create an `Istio VirtualService`, which allows the cluster to respond to **load-balancing health check requests** by <ins><b>forwarding the requests to the status endpoint</b></ins> on the Istio Ingress Gateway:
```yaml
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

* Patch `istio-ingress`,Istio Ingress Gateway created by GKE:
  * Change Service type: `LoadBalancer` -> `NodePort`
  * Annotate `cloud.google.com/neg: '{"ingress": true}'`

```json
kubectl -n gke-system patch svc istio-ingress \
    --type=json -p - <<EOF
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

:bulb: This changes existing `istio-ingress` as the following:
#container-native-loadbalancing-a-direct-way-to-expose-pod-endpoints-using-negsnetwork-endpoint-groups
  * Annotate `cloud.google.com/neg: '{"ingress": true}'`.
    This Creates [Ref.](https://cloud.google.com/kubernetes-engine/docs/how-to/container-native-load-balancing#create_service)
```sh
kubectl annotate svc istio-ingress -n gke-system cloud.google.com/neg='{"exposed_ports": {"80":{}}}'
```


```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: sayhello-healthcheck
spec:
  hosts:
  - "*"
  http:
  - match:
    - uri:
        prefix: /sayhello-service-nodeport
      # headers:
      #   end-user:
      #     exact: pydemia
    rewrite:
      uri: /healthy
    route:
    - destination:
        host: sayhello-service-nodeport
        port:
          number: 80
  - match:
    - uri:
        prefix: /v2
    route:
    - destination:
        host: sayhello-service-for-ingress
        port:
          number: 80
```