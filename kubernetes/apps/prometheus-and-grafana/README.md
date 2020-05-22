# Kubernetes Monitoring via `prometheus` and `grafana`

```sh
#kubectl -n istio-system get svc grafana
#kubectl -n istio-system port-forward $(kubectl -n istio-system get pod -l app=grafana -o jsonpath='{.items[0].metadata.name}') 3000:3000 &

$ kubectl -n knative-monitoring get svc grafana
NAME      TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)           AGE
grafana   NodePort   10.187.1.204   <none>        30802:30178/TCP   23h

$ kubectl -n knative-monitoring port-forward $(kubectl -n knative-monitoring get pod -l app=grafana -o jsonpath='{.items[0].metadata.name}') 3000:30178 &

$ kubectl port-forward --namespace knative-monitoring \
$(kubectl get pods --namespace knative-monitoring \
--selector=app=grafana --output=jsonpath="{.items..metadata.name}") \
3000

$ gcloud container clusters get-credentials kfserving-dev --region us-central1 --project ds-ai-platform \
 && kubectl port-forward --namespace istio-system $(kubectl get pod --namespace istio-system --selector="app=istio-ingressgateway,istio=ingressgateway,release=release-name" --output jsonpath='{.items[0].metadata.name}') 8080:15031

$ gcloud container clusters get-credentials kfserving-dev --region us-central1 --project ds-ai-platform \
 && kubectl port-forward --namespace knative-monitoring $(kubectl get pod --namespace istio-system --selector="app=istio-ingressgateway,istio=ingressgateway,release=release-name" --output jsonpath='{.items[0].metadata.name}') 8080:15031
```


```yaml
cat << EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: knative-services-gateway
  namespace: knative-monitoring
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      name: http-knative-service
      number: 80
      protocol: HTTP
    hosts:
    - "*"
  #   # - knative-grafana.${MY_DOMAIN}
  #   # - knative-prometheus.${MY_DOMAIN}
  #   # - knative-tekton.${MY_DOMAIN}
  # - port:
  #     number: 443
  #     name: https-knative-services
  #     protocol: HTTPS
  #   hosts:
  #   - "*"
  #   # - knative-grafana.${MY_DOMAIN}
  #   # - knative-prometheus.${MY_DOMAIN}
  #   tls:
  #     credentialName: ingress-cert-${LETSENCRYPT_ENVIRONMENT}
  #     mode: SIMPLE
  #     privateKey: sds
  #     serverCertificate: sds
# ---
# apiVersion: networking.istio.io/v1alpha3
# kind: DestinationRule
# metadata:
#   name: grafana
#   namespace: istio-system
# spec:
#   host: grafana.istio-system.svc.cluster.local
#   trafficPolicy:
#     tls:
#       mode: DISABLE
# ---
# apiVersion: networking.istio.io/v1alpha3
# kind: DestinationRule
# metadata:
#   name: grafana
#   namespace: istio-system
# spec:
#   host: grafana.istio-system.svc.cluster.local
#   trafficPolicy:
#     tls:
#       mode: DISABLE
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: grafana-virtual-service
  namespace: knative-monitoring
spec:
  hosts:
  - "*"
  gateways:
  - knative-services-gateway
  http:
  - match:
    - uri:
        prefix: /grafana
    rewrite:
      uri: /
    route:
    - destination:
        host: grafana.knative-monitoring.svc.cluster.local
        port:
          number: 3000
          # number: 30802
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: prometheus-virtual-service
  namespace: knative-monitoring
spec:
  hosts:
  - "*"
  gateways:
  - knative-services-gateway
  http:
  - match:
    - uri:
        prefix: /prometheus/
    rewrite:
      uri: /
    route:
    - destination:
        host: prometheus-system-np.knative-monitoring.svc.cluster.local
        port:
          number: 8080
EOF
```

## Create a new organization and an API Token

```sh
$ CLUSTER_GRAFANA=35.223.25.173/knative/grafana
$ curl http://$CLUSTER_GRAFANA/api/org
{"id":1,"name":"Main Org.","address":{"address1":"","address2":"","city":"","zipCode":"","state":"","country":""}}
```

```sh
# Create an org
# curl -X POST -H "Content-Type: application/json" -d '{"name":"apiorg"}' http://admin:admin@localhost:3000/api/orgs
$ curl -X POST -H "Content-Type: application/json" -d '{"name":"pydemia"}' http://admin:admin@$CLUSTER_GRAFANA/api/orgs
{"message":"Organization created","orgId":2}

# (Optional) Add your admin user to the org
$ curl -X POST -H "Content-Type: application/json" -d '{"loginOrEmail":"admin", "role": "Admin"}' http://admin:admin@$CLUSTER_GRAFANA/api/orgs/2/users
{"message":"User is already member of this organization"}

# Switch the org context for the Admin user to the new org
$ curl -X POST http://admin:admin@$CLUSTER_GRAFANA/api/user/using/2
{"message":"Active organization changed"}

# Create the API token
$ curl -X POST -H "Content-Type: application/json" -d '{"name":"pydemia-apikey", "role": "Admin"}' http://admin:admin@$CLUSTER_GRAFANA/api/auth/keys
{"name":"pydemia-apikey","key":"eyJrIjoiblU0ZXdLekliblZyN0lueG5vdTN5NzEwZTRDazZOM1ciLCJuIjoicHlkZW1pYS1hcGlrZXkiLCJpZCI6Mn0="}

# Create a dashboard
$ curl -X POST --insecure -H "Authorization: Bearer eyJrIjoiblU0ZXdLekliblZyN0lueG5vdTN5NzEwZTRDazZOM1ciLCJuIjoicHlkZW1pYS1hcGlrZXkiLCJpZCI6Mn0=" -H "Content-Type: application/json" -d '{
  "dashboard": {
    "id": null,
    "uid": "pydemia",
    "annotations": {
          "list":[]
      },
    "tags": [ "templated" ],
    "templating": {
        "list": []
    },
    "editable": true,
    "gnetId": null,
    "title": "Sample Dashboard-pydemia",
    "iteration": 1529322539820,
    "links":[],
    "panels": [{}],
    "rows": [
      {
      }
    ],
    "__inputs": [],
    "__requires": [],  
    "timezone": "browser",
    "schemaVersion": 6,
    "style": "dark",
    "version": 0
  },
  "inputs": [],
  "overwrite": false
}' http://$CLUSTER_GRAFANA/api/dashboards/db

{"id":15,"slug":"sample-dashboard-pydemia","status":"success","uid":"uid","url":"/d/uid/sample-dashboard-pydemia","version":1}

# Get the dashboard
$ curl -X GET -H "Accept: application/json;Content-Type: application/json;Authorization: Bearer eyJrIjoiblU0ZXdLekliblZyN0lueG5vdTN5NzEwZTRDazZOM1ciLCJuIjoicHlkZW1pYS1hcGlrZXkiLCJpZCI6Mn0=" http://admin:admin@$CLUSTER_GRAFANA/api/dashboards/uid/pydemia

{"meta":{"type":"db","canSave":true,"canEdit":true,"canAdmin":true,"canStar":true,"slug":"sample-dashboard-pydemia","url":"/d/pydemia/sample-dashboard-pydemia","expires":"0001-01-01T00:00:00Z","created":"2020-05-19T18:25:03Z","updated":"2020-05-19T18:25:03Z","updatedBy":"Anonymous","createdBy":"Anonymous","version":1,"hasAcl":false,"isFolder":false,"folderId":0,"folderTitle":"General","folderUrl":"","provisioned":false,"provisionedExternalId":""},"dashboard":{"__inputs":[],"__requires":[],"annotations":{"list":[]},"editable":true,"gnetId":null,"id":16,"iteration":1529322539820,"links":[],"panels":[{}],"rows":[{}],"schemaVersion":6,"style":"dark","tags":["templated"],"templating":{"list":[]},"timezone":"browser","title":"Sample Dashboard-pydemia","uid":"pydemia","version":1}}

$ curl -X GET -H "Accept: application/json;Content-Type: application/json;Authorization: Bearer eyJrIjoiblU0ZXdLekliblZyN0lueG5vdTN5NzEwZTRDazZOM1ciLCJuIjoicHlkZW1pYS1hcGlrZXkiLCJpZCI6Mn0=" http://admin:admin@$CLUSTER_GRAFANA/api/dashboards/home

# Delete the dashboard
$ curl -X DELETE -H "Content-Type: application/json" -d '{"name":"pydemia-apikey", "role": "Admin"}' http://admin:admin@$CLUSTER_GRAFANA/api/dashboards/db/sample-dashboard-pydemia 
{"message":"Dashboard Sample Dashboard-pydemia deleted","title":"Sample Dashboard-pydemia"}
```

kubectl -n knative-serving describe deploy controller 
kubectl get pods --namespace knative-monitoring
kubectl port-forward -n knative-monitoring $(kubectl get pods -n knative-monitoring -l=app=grafana --output=jsonpath="{.items..metadata.name}") 30802

```sh
GET /api/dashboards/home

```




# kubectl -n istio-system port-forward $(kubectl -n istio-system get pod -l app=grafana -o jsonpath='{.items[0].metadata.name}') 3000:3000 &
kubectl -n knative-monitoring port-forward $(kubectl -n knative-monitoring get pod -l app=grafana -o jsonpath='{.items[0].metadata.name}') 3000:3000


echo '{
  "dashboard": {
    "annotations": {
          "list":[]
      },
    "editable": true,
    "gnetId": null,
    "graphTooltip": 0,
    "id": null,
    "iteration": 1529322539820,
    "links":[],
    "panels": [{}],
    "schemaVersion": 16,
    "style": "dark",
    "tags": [],
    "templating": {
        "list": []
    },
    "time": {},
    "timepicker": {},
    "timezone": "",
    "title": "name of the dashboard",
    "uid": "uid",
    "version": 1,
    "__inputs": [],
    "__requires": []
  },
  "inputs": [],
  "overwrite": false
}' > grafana-dashboard-import.json

```yaml
cat << EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: knative-services-gateway
  namespace: knative-monitoring
spec:
  selector:
    istio: ingressgateway
  servers:
  - hosts:
    - "*"
    port:
      name: http-knative-service
      number: 80
      protocol: HTTP
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: prometheus-virtual-service
  namespace: knative-monitoring
spec:
  hosts:
  - "*"
  gateways:
  - knative-services-gateway
  http:
  - match:
    - uri:
        prefix: /prometheus/
    rewrite:
      uri: /
    route:
    - destination:
        host: prometheus-system-np.knative-monitoring.svc.cluster.local
        port:
          number: 8080
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: grafana-virtual-service
  namespace: knative-monitoring
spec:
  hosts:
  - "*"
  gateways:
  - knative-services-gateway
  http:
  - match:
    # - method:
    #   exact: GET
    - uri:
        prefix: /grafana/
    rewrite:
      uri: /
    route:
    - destination:
        host: grafana.knative-monitoring.svc.cluster.local
        port:
          number: 30802
EOF
grafana.knative-monitoring.svc.cluster.local
```

Restart Pod
```sh
kubectl -n knative-monitoring rollout restart deployment grafana
```

`grafana-custom-config`
```yaml
apiVersion: v1
kind: ConfigMap
name: grafana-custom-config
  namespace: knative-monitoring
data:
  custom.ini: |
    # You can customize Grafana via changing context of this field.
    [auth.anonymous]
    # enable anonymous access
    enabled = true
    [server]
    protocol = http
    domain = 35.223.25.173
    http_port = 3000
    root_url = %(protocol)s://%(domain)s:%(http_port)s/grafana/
    serve_from_sub_path = true
```


---

## Grafana on Istio

```sh
$ istioctl manifest apply --set values.grafana.enabled=true
```

```sh
$ kubectl -n istio-system get svc prometheus
$ kubectl -n istio-system get svc grafana
```

```
$ kubectl -n istio-system port-forward $(kubectl -n istio-system get pod -l app=grafana -o jsonpath='{.items[0].metadata.name}') 3000:3000 &
$ istioctl dashboard prometheus
$ istioctl dashboard grafana
```


## Kiali on Istio

* `bash`
```bash
# Username
$ KIALI_USERNAME=$(read -p 'Kiali Username: ' uval && echo -n $uval | base64)

# Passphrase
$ KIALI_PASSPHRASE=$(read -sp 'Kiali Passphrase: ' pval && echo -n $pval | base64)
```

* `zsh`
```zsh
$ KIALI_USERNAME=$(read '?Kiali Username: ' uval && echo -n $uval | base64)
$ KIALI_PASSPHRASE=$(read -s "?Kiali Passphrase: " pval && echo -n $pval | base64)
```

Then, create a secret:
```sh
$ NAMESPACE=istio-system
$ kubectl create namespace $NAMESPACE
$ cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: kiali
  namespace: $NAMESPACE
  labels:
    app: kiali
type: Opaque
data:
  username: $KIALI_USERNAME
  passphrase: $KIALI_PASSPHRASE
EOF
secret/kiali created
```

Install `kiali` via `istioctl`

```sh
$ istioctl manifest apply --set values.kiali.enabled=true \
  --set "values.kiali.dashboard.grafanaURL=http://grafana:3000"
```

istioctl manifest apply --set values.kiali.enabled=true \
  --set values.grafana.enabled=true

Generating a service graph
```sh
$ kubectl -n istio-system get svc kiali
```

---

# Ingress via `nginx`

```sh
curl -sL https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-0.32.0/deploy/static/provider/cloud/deploy.yaml -o nginx-ingress-controller.yaml && \
kubectl apply -f nginx-ingress-controller.yaml
```

```yaml
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1beta1
# Ingress
kind: Ingress
metadata:
  name: monitoring-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    kubernetes.io/ingress.class: nginx
    # certmanager.k8s.io/cluster-issuer: letsencrypt
    # nginx.ingress.kubernetes.io/ssl-redirect: "true"
    # kubernetes.io/tls-acme: 'true'
    # nginx.ingress.kubernetes.io/tls-acme: 'true'
spec: 
  rules:
  - http:
      paths:
      - path: /*
        backend:
          serviceName: ingress-nginx
          servicePort: 80
      - path: /monitoring/knative/grafana/
        backend:
          serviceName: grafana.knative-monitoring.svc.cluster.local
          servicePort: 3000
      - path: /monitoring/knative/prometheus/
        backend:
          serviceName: prometheus-system-np.knative-monitoring.svc.cluster.local
          servicePort: 9090
      - path: /monitoring/istio/kiali/
        backend:
          serviceName: kiali.istio-system.svc.cluster.local
          servicePort: 20001
      - path: /monitoring/istio/grafana/
        backend:
          serviceName: grafana.istio-system.svc.cluster.local
          servicePort: 3000
      - path: /monitoring/istio/prometheus/
        backend:
          serviceName: prometheus.istio-system.svc.cluster.local
          servicePort: 9090
EOF
```

```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: http
  - name: https
    port: 443
    protocol: TCP
    targetPort: https
  - name: http-grafana
    nodePort: 30802
    port: 80
    protocol: TCP
    targetPort: 30802
  - name: http-prometheus
    port: 8080
    protocol: TCP
    targetPort: 8080
EOF
```
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

kubectl -n knative-monitoring expose svc grafana \
        --type ExternalName  --target-port 3000

```yaml
kubectl -n knative-monitoring patch svc grafana \
    --type=json -p - <<EOF
[
  {
    "op": "replace",
    "path": "/spec/type",
    "value": "ExternalName"
  },
  {
    "op": "remove",
    "path": "/status"
  }
]
EOF
,
  {
    "op": "add",
    "path": "/spec/externalName",
    "value": "grafana.knative-monitoring.svc.cluster.local"
  }
kubectl -n knative-monitoring patch svc prometheus-system-np \
    --type=json -p - <<EOF
[
  {
    "op": "replace",
    "path": "/spec/type",
    "value": "ExternalName"
  },
  {
    "op": "add",
    "path": "/spec/externalName",
    "value": "prometheus-system-np.knative-monitoring.svc.cluster.local"
  }
]
EOF
kubectl -n istio-system patch svc kiali \
    --type=json -p - <<EOF
[
  {
    "op": "replace",
    "path": "/spec/type",
    "value": "ExternalName"
  },
  {
    "op": "add",
    "path": "/spec/externalName",
    "value": "kiali.istio-system.svc.cluster.local"
  }
]
EOF
kubectl -n istio-system patch svc grafana \
    --type=json -p - <<EOF
[
  {
    "op": "replace",
    "path": "/spec/type",
    "value": "ExternalName"
  },
  {
    "op": "add",
    "path": "/spec/externalName",
    "value": "grafana.istio-system.svc.cluster.local"
  }
]
EOF
kubectl -n istio-system patch svc prometheus \
    --type=json -p - <<EOF
[
  {
    "op": "replace",
    "path": "/spec/type",
    "value": "ExternalName"
  },
  {
    "op": "add",
    "path": "/spec/externalName",
    "value": "prometheus.istio-system.svc.cluster.local"
  }
]
EOF
```