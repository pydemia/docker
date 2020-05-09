# Exposing

  * [Exposing](exposing/README.md)
    * [**Service**](): An Abstract way to expose APPs, running on a set of Pods.
      * `ClusterIP` type: within Cluster
      * `NodePort` type: rely on Node, if Node(VM) IP is accessible
      * `LoadBalancer` type: by given (IP, DomainName) in Cloud
    * [**Ingress**](): L7 with LoadBalancer

---
## Inside Docker Networking

Default docker network is: `bridge`
```sh
$ nmcli device status
DEVICE           TYPE      STATE         CONNECTION         
docker0          bridge    connected     docker0            
enp0s31f6        ethernet  connected     Wired connection 1 
wlx0013ef601444  wifi      disconnected  --                 
veth647d6fd      ethernet  unmanaged     --                 
veth7a59c27      ethernet  unmanaged     --                 
lo               loopback  unmanaged     --                 
```

Connect a docker to another: `--network` and `--link <NAME>:<ALIAS>`.
```sh
$ docker run --name dbserver --network bridge -e MYSQL_ALLOW_EMPTY_PASSWORD=yes mysql:latest --default-authentication-plugin=mysql_native_password
$ docker run --name webserver --network bridge -p 8080:80 --link dbserver:mdb nginx:latest
```

Show it:
```sh
$ docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Networks}}\t{{.Ports}}'
CONTAINER ID        IMAGE               NAMES               NETWORKS            PORTS
e22ce14ae3dd        nginx:latest        webserver           bridge              80/tcp
ed360a6f7238        mysql:latest        dbserver            bridge              3306/tcp, 33060/tcp, 0.0.0.0:8080->80/tcp
```

Now `dbserver` can be accessible from `webserver`, using `mdb:3306`.

```sh
docker exec -it webserver /bin/bash
# apt update && apt install default-mysql-client -y
mysql -h mdb -P 3306 -u root
```

---
## Service

<https://cloud.google.com/kubernetes-engine/docs/how-to/exposing-apps>

For test, we use a docker image `gcr.io/google-samples/hello-app:2.0`. Test it locally.
```sh
$ docker run -rm -p 8080:8080 gcr.io/google-samples/hello-app:2.0

# Get the output
$ curl localhost:8080
Hello, world!
Version: 2.0.0
Hostname: efec64468928
```

### Deployment for `sayhello` app

```sh
$ kubectl apply -f sayhello-deployment.yaml
deployment.apps/sayhello-deployment created
```

```yaml
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sayhello-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sayhello
  template:
    metadata:
      name: sayhello-8080server
      labels:
        app: sayhello
    spec:
      containers:
      - name: hello-container
        image: "gcr.io/google-samples/hello-app:2.0"
        ports:
        - containerPort: 8080
EOF
```

```sh
$ kubectl get pods -o wide
NAME                                  READY   STATUS    RESTARTS   AGE     IP
sayhello-deployment-db9bc6b9f-bqf9t   1/1     Running   0          21s     10.56.0.14
sayhello-deployment-db9bc6b9f-n42tv   1/1     Running   0          21s     10.56.2.9
```

Access it:
```sh
$ kubectl run -i --tty --rm debug1 --image=marketplace.gcr.io/google/ubuntu1804 --restart=Never -- curl 10.56.0.14:8080
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-bqf9t
pod "debug1" deleted
$ kkubectl run -i --tty --rm debug2 --image=marketplace.gcr.io/google/ubuntu1804 --restart=Never -- curl 10.56.2.9:8080
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-n42tv
pod "debug2" deleted
```


### `ClusterIP`: using an app(it can be a set of *Pods*) inside.

| ![](clusterip.jpg) |
| ----- |

`sayhello-service-clusterip.yaml`
```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: sayhello-service-clusterip
spec:
  selector:
    app: sayhello
  ports:
  - name: webport
    protocol: TCP
    # port: Port that Service will be using
    port: 80
    # targetPort: Deployed Container's Port = containerPort
    targetPort: 8080
  type: ClusterIP
EOF
```

```sh
$ kubectl apply -f sayhello-service-clusterip.yaml
service/sayhello-service-clusterip created

$ kubectl get services  # {services, svc}
NAME                         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
kubernetes                   ClusterIP   10.187.0.1     <none>        443/TCP   13h
sayhello-service-clusterip   ClusterIP   10.187.6.190   <none>        80/TCP    2m15s
```

Access it, using `CLUSTER-IP=10.187.6.190` and Service `NAME`:
```sh
# CLUSTER-IP=10.187.6.190
$ kubectl run -i --tty --rm debug1 --image=marketplace.gcr.io/google/ubuntu1804 --restart=Never -- curl 10.187.6.190:80
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-n42tv
pod "debug1" deleted

# Service Name
$ kubectl run -i --tty --rm debug2 --image=marketplace.gcr.io/google/ubuntu1804 --restart=Never -- curl sayhello-service-clusterip:80
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-bqf9t
pod "debug2" deleted
```

In case Service's Label Selector(`spec.selector`) and Pod's Label(`metadata.labels`) are matched,  
Kubernetes creates an Endpoint that has the same name as your Service.
```sh
$ kubectl get endpoints  # {endpoints, ep}
NAME                         ENDPOINTS                        AGE
kubernetes                   172.31.1.34:443                  15h
sayhello-service-clusterip   10.56.0.14:8080,10.56.2.9:8080   163m
```

### `NodePort`: using an app(it can be a set of *Pods*) through *Nodes*.

| ![](nodeport.jpg) |
| ----- |

`sayhello-service-nodeport.yaml`
```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: sayhello-service-nodeport
spec:
  selector:
    app: sayhello
  ports:
  - name: webport
    protocol: TCP
    # port: Port that Service will be using
    port: 80
    # targetPort: Deployed Container's Port = containerPort
    targetPort: 8080
  ################ ClusterIP -> NodePort
  type: NodePort
EOF
```

```sh
$ kubectl apply -f sayhello-service-nodeport.yaml
service/sayhello-service-nodeport created

$ kubectl get svc
NAME                         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes                   ClusterIP   10.187.0.1     <none>        443/TCP        16h
sayhello-service-clusterip   ClusterIP   10.187.6.190   <none>        80/TCP         178m
sayhello-service-nodeport    NodePort    10.187.5.22    <none>        80:30983/TCP   82s

# 80   : Port on Service, not Pod's(container).
# 30983: Port on Node's (all VMs having Pods).
```

Access it, with `CLUSTER-IP` and *Nodes* `(INTERNAL-IP, EXTERNAL-IP)`(if not a private cluster).

1. `CLUSTER-IP`, as `ClusterIP` Services:
```sh
$ kubectl get svc
NAME                         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes                   ClusterIP   10.187.0.1     <none>        443/TCP        16h
sayhello-service-clusterip   ClusterIP   10.187.6.190   <none>        80/TCP         178m
sayhello-service-nodeport    NodePort    10.187.5.22    <none>        80:30983/TCP   82s
```

```sh
# CLUSTER-IP=10.187.5.22
$ kubectl run -i --tty --rm debug1 --image=marketplace.gcr.io/google/ubuntu1804 --restart=Never -- curl 10.187.5.22:80
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-bqf9t
pod "debug1" deleted

# Service Name
$ kubectl run -i --tty --rm debug2 --image=marketplace.gcr.io/google/ubuntu1804 --restart=Never -- curl sayhello-service-nodeport:80
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-bqf9t
pod "debug2" deleted
```

2. `(INTERNAL-IP, EXTERNAL-IP)`, as VM:

```sh
$ kubectl get nodes -o wide
NAME                                           STATUS   ROLES    AGE   INTERNAL-IP    EXTERNAL-IP
gke-kfserving-dev-default-pool-08499930-wwz8   Ready    <none>   16h   10.128.2.215   34.70.66.169
gke-kfserving-dev-default-pool-3477a340-fl90   Ready    <none>   16h   10.128.2.218   34.68.174.165
gke-kfserving-dev-default-pool-5ca12738-qbhk   Ready    <none>   16h   10.128.2.10    35.23.193.10
```

2-1. At this time, we can `curl` directly because `EXTERNAL-IP` is opened.
```sh
# 30983, NOT 80
$ curl 34.70.66.169:30983

$ curl 34.68.174.165:30983

$ curl 35.23.193.10:30983
```

2-2. At the same time, we can `curl` inside the `vpc` or the private network the cluster Node exists.
***`INTERNAL-IP` is the private IP of the Node(VM)**, not the IP inside the cluster(it's `CLUSTER-IP`).
```sh
$ curl 10.128.2.215:30983

$ curl 10.128.2.218:30983

$ curl 10.128.2.10:30983
```

:warning: **Most clusters shoud have <font style="color:red "><b>private IP</b></font> and <font style="color:red"><b>firewall</b></font>** options. so  
* **2-1** is impossible because it have only <font style="color:red "><b>private IPs</b></font>. ~~`EXTERNAL-IP`~~
* **2-2** should not be allowed with <font style="color:red "><b>Firewall on port</b></font> ~~`30983`~~.

so we need to have an exposed Endpoint allowed to external access.  
There is a two options:
  * Direct way: Each Service has **HTTP/s Endpoint** of Cloud Provider, by using `LoadBalancer(HTTP or TCP/UDP)` type.
  * Indirect way: Use `Ingress` object to manage All incoming requests together, as unified.


### `LoadBalancer`: allowed way to access `NodePort`

| ![](loadbalancer.jpg) |
| ----- |

`sayhello-service-loadbalancer.yaml`
```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: sayhello-service-loadbalancer
spec:
  selector:
    app: sayhello
  ports:
  - name: webport
    protocol: TCP
    # port: Port that Service will be using
    port: 80
    # targetPort: Deployed Container's Port = containerPort
    targetPort: 8080
  ################ NodePort -> LoadBalancer
  type: LoadBalancer
EOF
```

```sh
$ kubectl apply -f sayhello-service-loadbalancer.yaml
service/sayhello-service-loadbalancer created

$ kubectl get svc
NAME                            TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes                      ClusterIP      10.187.0.1     <none>        443/TCP        17h
sayhello-service-clusterip      ClusterIP      10.187.6.190   <none>        80/TCP         4h10m
sayhello-service-loadbalancer   LoadBalancer   10.187.12.31   <pending>     80:32146/TCP   19s
sayhello-service-nodeport       NodePort       10.187.5.22    <none>        80:30983/TCP   73m

# <pending>: Work-in-progress, HTTP/s LoadBalancer is creating...

$ kubectl get svc
NAME                            TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)        AGE
kubernetes                      ClusterIP      10.187.0.1     <none>          443/TCP        17h
sayhello-service-clusterip      ClusterIP      10.187.6.190   <none>          80/TCP         4h11m
sayhello-service-loadbalancer   LoadBalancer   10.187.12.31   35.223.25.173   80:32146/TCP   109s
sayhello-service-nodeport       NodePort       10.187.5.22    <none>          80:30983/TCP   74m

# 35.223.25.173: Assigned and allowed EXTERNAL-IP, "HTTP/s" with 80, 8080, and 443 only.
# <https://cloud.google.com/load-balancing/docs/https#open_ports>

# 80   : Port on Service, opened.
# 32146: Port on Node's (all VMs having Pods), load-balanced.
```

Access it, **ANYWHERE**:
```sh
$ curl 35.223.25.173:80
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-n42tv
```

### (Optional) Network LoadBalancer(TCP/UDP LoadBalancer)

`sayhello-service-networkloadbalancer.yaml`
```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: sayhello-service-networkloadbalancer
spec:
  selector:
    app: sayhello
  ports:
  - name: webport
    protocol: TCP
    ################ custom port, not in (80, 8080, 443)
    port: 63214
    # targetPort: Deployed Container's Port = containerPort
    targetPort: 8080
  # LoadBalancer
  type: LoadBalancer
EOF
```

```sh
$ kubectl apply -f sayhello-service-networkloadbalancer.yaml
service/sayhello-service-networkloadbalancer created

$ kubectl get svc
NAME                                   TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)           AGE
kubernetes                             ClusterIP      10.187.0.1     <none>          443/TCP           17h
sayhello-service-clusterip             ClusterIP      10.187.6.190   <none>          80/TCP            4h26m
sayhello-service-loadbalancer          LoadBalancer   10.187.12.31   35.223.25.173   80:32146/TCP      16m
sayhello-service-networkloadbalancer   LoadBalancer   10.187.3.20    35.184.44.79    63214:32078/TCP   57s
sayhello-service-nodeport              NodePort       10.187.5.22    <none>          80:30983/TCP      89m
```
gcloud compute url-maps list

Access it, **ANYWHERE**:
```sh
$ curl 35.184.44.79:63214
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-bqf9t
```

List the `forwarding-rules`, and you can find LoadBalancer`s IPs.
```sh
$ gcloud compute forwarding-rules list
$ gcloud compute forwarding-rules list| grep '35.184.44.79\|35.223.25.173'
NAME                REGION       IP_ADDRESS      IP_PROTOCOL  TARGET
b35ea881cff         us-central1  35.223.25.173   TCP          us-central1/targetPools/a191dc88
8b4c1b84cd5         us-central1  35.184.44.79    TCP          us-central1/targetPools/a9c76274
```

### use `kubectl expose`:

```sh
DEPLOY_YAML="sayhello-service-loadbalancer.yaml"
$ kubectl expose -f DEPLOY_YAML
```

```sh
DEPLOY_NAME="sayhello-service-loadbalancer"
SERVICE_TYPE="LoadBalancer"
PROTOCOL="TCP"  # TCP|UDP|SCTP
SERVICE_PORT="63214"
TARGET_PORT="8080"

$ kubectl expose deployment \
    $DEPLOY_YAML \
    --name $DEPLOY_NAME \
    --type $SERVICE_TYPE \
    --protocol TCP
    --port $SERVICE_PORT \
    --target-port $TARGET_PORT
    #--external-ip
```

---

### `ExternalName`: A groundwork for `Ingress`

`sayhello-service-externalname.yaml`
```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: sayhello-service-externalname
spec:
  selector:
    app: sayhello
  ports:
  - name: webport
    protocol: TCP
    ################ custom port, not in (80, 8080, 443)
    port: 51478
    # targetPort: Deployed Container's Port = containerPort
    targetPort: 8080
  # LoadBalancer
  type: ExternalName
  externalName: sayhello-service-externalname.default.svc.cluster.local
EOF
```

```sh
$ kubectl apply -f sayhello-service-externalname.yaml
service/sayhello-service-externalname created

$ kubectl get svc
NAME                                   TYPE           CLUSTER-IP     EXTERNAL-IP                                               PORT(S)           AGE
kubernetes                             ClusterIP      10.187.0.1     <none>                                                    443/TCP           18h
sayhello-service-clusterip             ClusterIP      10.187.6.190   <none>                                                    80/TCP            4h58m
sayhello-service-externalname          ExternalName   <none>         sayhello-service-externalname.default.svc.cluster.local   51478/TCP         58s
sayhello-service-loadbalancer          LoadBalancer   10.187.12.31   35.223.25.173                                             80:32146/TCP      48m
sayhello-service-networkloadbalancer   LoadBalancer   10.187.3.20    35.184.44.79                                              63214:32078/TCP   33m
sayhello-service-nodeport              NodePort       10.187.5.22    <none>                                                    80:30983/TCP      121m
```

```sh
$ curl sayhello-service-externalname.default.svc.cluster.local
curl: (6) Could not resolve host: sayhello-service-externalname.default.svc.cluster.local
```

:warning: It cannot be resolved **because any DNS doesn't find a proper IP address for that name.**
We can use `Ingress` and give a proper domain name for that type of service.

### `Ingress`: an unified URL Endpoint for Kubernetes Cluster

Not multiple Endpoints, use `Ingress` to manage.

| ![]() |
| ----- |
