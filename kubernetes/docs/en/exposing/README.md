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


### `ClusterIP`: using an app(it can be a set of Pods) inside.

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
  - protocol: TCP
    # port: Port that Service will be using
    port: 80
    # targetPort: Deployed Container's Port = containerPort
    targetPort: 8080
  type: ClusterIP
EOF
```

```sh
$ kubectl apply -f sayhello-service-clusterip.yaml
$ kubectl get services
NAME                         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
kubernetes                   ClusterIP   10.187.0.1     <none>        443/TCP   13h
sayhello-service-clusterip   ClusterIP   10.187.6.190   <none>        80/TCP    2m15s
```

Access it: using `CLUSTER-IP=10.187.6.190` and Service `NAME`
```sh
# CLUSTER-IP=10.187.6.190
$ kubectl run -i --tty --rm debug --image=marketplace.gcr.io/google/ubuntu1804 --restart=Never -- curl 10.187.6.190:80
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-n42tv
pod "debug" deleted

# Service Name
$ kubectl run -i --tty --rm debug --image=marketplace.gcr.io/google/ubuntu1804 --restart=Never -- curl sayhello-service-clusterip:80
Hello, world!
Version: 2.0.0
Hostname: sayhello-deployment-db9bc6b9f-bqf9t
pod "debug" deleted
```

## Ingress