# Kubernetes Commands

## `kubectl`

```bash
$ kubectl [commands]
$ kubectl [commands-verbs] [resource-name]
$ kubectl [commands-verbs] ...
```

### Cluster
```bash
$ kubectl reset
$ kubectl init ...
$ kubectl drain [NODE]
```

### Deploying
```bash
$ kubectl apply -f [DEPLOY.yaml]
$ kubectl create --edit -f [[DEPLOY.yaml]]

$ kubectl delete -f [DEPLOY.yaml]

$ kubectl run -f [DEPLOY.yaml]
```

### Monitoring & Logging
```bash
$ kubectl cluster-info
$ kubectl top
$ kubectl api-resources
$ kubectl api-versions
$ kubectl auth
$ kubectl get svc
$ ubectl config get-clusters
$ kubectl config current-context

$ kubectl explain [RESOURCE]
$ kubectl get [RESOURCE]
$ kubectl logs
$ kubectl describe
```

---
# Use-cases

```bash
$ kubectl apply -f kubernetes-dashboard-v2.0.0.yaml
$ kubectl delete -f kubernetes-dashboard-v2.0.0.yaml
$ kubectl proxy
$ kubectl get secret,sa,role,rolebinding,services,deployments --namespace=kubernetes-dashboard | grep dashboard


$ kubectl get secret
$ kubectl describe secrets kubernetes-bashboard

$ kubectl get secret -n kubernetes-dashboard
$ kubectl describe secrets kubernetes-dashboard-token-mbwwc -n kubernetes-dashboard
$ kubectl describe secrets -n kubernetes-dashboard $(kubectl get serviceaccount kubernetes-dashboard -n kubernetes-dashboard -o jsonpath="{.secrets[0].name}")
$ kubectl get secret -n kubernetes-dashboard $(kubectl get serviceaccount kubernetes-dashboard -n kubernetes-dashboard -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode

$ echo `kubectl get secret -n kubernetes-dashboard $(kubectl get serviceaccount kubernetes-dashboard -n kubernetes-dashboard -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode`
$ echo `kubectl get secret -n kubernetes-dashboard $(kubectl get sa -n kubernetes-dashboard -o jsonpath='{.items[?(@.metadata.name=="kubernetes-dashboard")].secrets[0].name}') -o jsonpath="{.data.token}" | base64 --decode`

# config the cluster to new context
$ kubectl config set-credentials kubernetes-dashboard-user --token=$(kubectl get secret -n kubernetes-dashboard $(kubectl get serviceaccount kubernetes-dashboard -n kubernetes-dashboard -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode)
$ kubectl config get-clusters
$ kubectl config set-context kbdashboard-context --user=kubernetes-dashboard-user
$ kubectl config get-contexts
CURRENT   NAME                          CLUSTER      AUTHINFO                    NAMESPACE
          kbdashboard-context                        kubernetes-dashboard-user
*         kubernetes-admin@kubernetes   kubernetes   kubernetes-admin
$ kubectl config use-context kbdashboard-context
$ kubectl config use-context kubernetes-admin@kubernetes


$ kubectl create sa kbmonitor -n kubernetes-dashboard
$ kubectl create namespace kubernetes-dashboard
$ kubectl create secret generic kubernetes-dashboard-certs --from-file=$HOME/certs -n kubernetes-dashboard

$ kubectl get sa kubernetes-dashboard -o yaml

$ kubectl get events -n kubernetes-dashboard
$ kubectl describe services kubernetes-dashboard -n kubernetes-dashboard

$ kubectl get pods -n kubernetes-dashboard -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'|grep kubernetes-dashboard

$ kubectl logs -n kubernetes-dashboard $(kubectl get pods -n kubernetes-dashboard -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'|grep kubernetes-dashboard | awk '{print $1}')

$ kubectl describe pods -n kubernetes-dashboard $(kubectl get pods -n kubernetes-dashboard -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'|grep kubernetes-dashboard | awk '{print $1}')

$ kubectl get secret -n kubernetes-dashboard $(kubectl get serviceaccount kubernetes-dashboard -n kubernetes-dashboard -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode

$ kubectl get sa -n kubernetes-dashboard -o jsonpath='{.items[?(@.metadata.name!="default")].metadata.name}'
$ kubectl get sa -n kubernetes-dashboard -o jsonpath='{.items[?(@.metadata.name=="kubernetes-dashboard")].secrets[0].name}'
```

[JSONPath](https://kubernetes.io/docs/reference/kubectl/jsonpath/)


```bash
$ kubectl get nodes --as system:serviceaccount:default:kubernetes-dashboard
$ kubectl get services --as system:serviceaccount:default:kubernetes-dashboard
$ kubectl get services --as system:serviceaccount:default:kubernetes-dashboard --all-namespaces

```

```bash
$ kubectl config set-credentials 
```

kubectl create clusterrolebinding kubernetes-dashboard --clusterrole=cluster-admin --serviceaccount=kube-system:kubernetes-dashboard
