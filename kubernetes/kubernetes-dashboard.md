# Kubernetes Dashboard

[github-Kubernetes/dashboard](https://github.com/kubernetes/dashboard)


**_IMPORTANT_**: Read the Access Control guide before performing any further steps.  
The default Dashboard deployment contains a minimal set of RBAC privileges needed to run.  

* Deploy it:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```

or

```bash
wget https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml \
  -O kubernetes-dashboard-v2.0.0.yaml
kubectl apply -f kubernetes-dashboard-v2.0.0.yaml
```

kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.6.0/src/deploy/kubernetes-dashboard.yaml


```bash
wget https://raw.githubusercontent.com/kubernetes/dashboard/v1.6.0/src/deploy/kubernetes-dashboard.yaml \
  -O kubernetes-dashboard-v1.6.0.yaml
kubectl apply -f kubernetes-dashboard-v1.6.0.yaml
```


```ascii
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
secret/kubernetes-dashboard-certs created
secret/kubernetes-dashboard-csrf created
secret/kubernetes-dashboard-key-holder created
configmap/kubernetes-dashboard-settings created
role.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrole.rbac.authorization.k8s.io/kubernetes-dashboard created
rolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
service/dashboard-metrics-scraper created
deployment.apps/dashboard-metrics-scraper created


NAMESPACE              NAME                                         READY   STATUS    RESTARTS   AGE
...
kubernetes-dashboard   dashboard-metrics-scraper-76679bc5b9-vd9rg   1/1     Running   0          21m
kubernetes-dashboard   kubernetes-dashboard-7f9fd5966c-g59xx        0/1     Error     8          21m
```

* Access it:

```bash
kubectl proxy

Starting to serve on 127.0.0.1:8001
```
 Now access dashboard at:
 <http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/>

* Stop it:

```bash
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```
