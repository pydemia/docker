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
        prefix: /knative/grafana/
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



