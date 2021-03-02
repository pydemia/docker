# Install `RabbitMQ` on a Kubernetes Cluster

RERUIRE: `helm`([Set up](../apps/helm/README.md#create-tiller-service-account-and-assign-cluster-admin-role-then-initiate-helm--install-tiller))

* Namespace: ~~`ifsvc`~~ `rabbit`

[Ref](https://hub.helm.sh/charts/bitnami/rabbitmq)

```sh
$ kubectl create ns rabbitmq
namespace/rabbitmq created

$ kubectl label ns rabbitmq istio-injection=enabled
namespace/rabbitmq labeled

$ helm repo add bitnami https://charts.bitnami.com/bitnami
"bitnami" has been added to your repositories

$ helm fetch bitnami/rabbitmq 

$ tar -xf rabbitmq-6.25.13.tgz  # untar in rabbitmq

# helm install --name kfs-rabbitmq bitnami/rabbitmq --namespace rabbitmq
# helm del --purge kfs-rabbitmq
$ helm install --name rabbitmq \
  --set rabbitmq.username=kfs,rabbitmq.password=kfs,rabbitmq.erlangCookie=secretcookie \
    bitnami/rabbitmq \
    --namespace rabbitmq
```

Then, the output would be:

```ascii
NAME:   rabbitmq
LAST DEPLOYED: Sun May 31 14:51:47 2020
NAMESPACE: rabbitmq
STATUS: DEPLOYED

RESOURCES:
==> v1/ConfigMap
NAME                   DATA  AGE
rabbitmq-config        2     1s
rabbitmq-healthchecks  2     1s

==> v1/Pod(related)
NAME        READY  STATUS   RESTARTS  AGE
rabbitmq-0  0/2    Pending  0         1s

==> v1/Role
NAME                      AGE
rabbitmq-endpoint-reader  1s

==> v1/RoleBinding
NAME                      AGE
rabbitmq-endpoint-reader  1s

==> v1/Secret
NAME      TYPE    DATA  AGE
rabbitmq  Opaque  2     1s

==> v1/Service
NAME               TYPE       CLUSTER-IP    EXTERNAL-IP  PORT(S)                                AGE
rabbitmq           ClusterIP  10.122.8.238  <none>       4369/TCP,5672/TCP,25672/TCP,15672/TCP  1s
rabbitmq-headless  ClusterIP  None          <none>       4369/TCP,5672/TCP,25672/TCP,15672/TCP  1s

==> v1/ServiceAccount
NAME      SECRETS  AGE
rabbitmq  2        1s

==> v1/StatefulSet
NAME      READY  AGE
rabbitmq  0/1    1s


NOTES:

** Please be patient while the chart is being deployed **

Credentials:

    echo "Username      : kfs"
    echo "Password      : $(kubectl get secret --namespace rabbitmq rabbitmq -o jsonpath="{.data.rabbitmq-password}" | base64 --decode)"
    echo "ErLang Cookie : $(kubectl get secret --namespace rabbitmq rabbitmq -o jsonpath="{.data.rabbitmq-erlang-cookie}" | base64 --decode)"

RabbitMQ can be accessed within the cluster on port  at rabbitmq.rabbitmq.svc.cluster.local

To access for outside the cluster, perform the following steps:

To Access the RabbitMQ AMQP port:

    echo "URL : amqp://127.0.0.1:5672/"
    kubectl port-forward --namespace rabbitmq svc/rabbitmq 5672:5672

To Access the RabbitMQ Management interface:

    echo "URL : http://127.0.0.1:15672/"
    kubectl port-forward --namespace rabbitmq svc/rabbitmq 15672:15672

```

Wait for all service is on:

```sh
$ kubectl -n rabbitmq get svc

NAME                TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                                 AGE
rabbitmq            ClusterIP   10.122.8.238   <none>        4369/TCP,5672/TCP,25672/TCP,15672/TCP   7m46s
rabbitmq-headless   ClusterIP   None           <none>        4369/TCP,5672/TCP,25672/TCP,15672/TCP   7m46s
```

* AMQP Port: `5672`
* Monitoring Dashboard: `15672`


### Expose RabbitMQ
```sh
$ kubectl apply -f expose-rabbitmq-knative-ingress-gateway.yaml
virtualservice.networking.istio.io/rabbitmq-vs created
gateway.networking.istio.io/rabbitmq-amqp-gateway created
virtualservice.networking.istio.io/rabbitmq-amqp-vs created
```

* DASHBOARD: `http://kfs.pydemia.org/rabbitmq/dashboard/`
* AMQP PORT `amqp://kfs.pydemia.org/rabbitmq/amqp/`

```sh
$ kubectl -n rabbitmq get svc

NAME                TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                                 AGE
rabbitmq            ClusterIP   10.122.8.238   <none>        4369/TCP,5672/TCP,25672/TCP,15672/TCP   7h37m
rabbitmq-headless   ClusterIP   None           <none>        4369/TCP,5672/TCP,25672/TCP,15672/TCP   7h37m
```

### (Optional) Start RabbitMQ with Docker

```sh
docker run --hostname rmq \
    -p 5672:5672 \
    -p 8080:15672 \
    -e RABBITMQ_DEFAULT_USER=guest \
    -e RABBITMQ_DEFAULT_PASS=guest \
    --name rabbitmq \
    rabbitmq:3-management
```

---
## Install `celery`

```sh
# conda activate kfserving
pip install celery
```
### Build an celery app

```sh
celery_demo
├── celery.py  # It's name should be `celery.py`
├── run_tasks.py
└── tasks.py
```

If `celery.py` not exist, you will meet this message:

```ascii
Error: 
Unable to load celery application.
Module 'celery_demo' has no attribute 'celery'
```


### Run the celery worker server
```sh
$ celery -A celery_demo worker --loglevel=info

 -------------- celery@pydemia-server v4.4.2 (cliffs)
--- ***** ----- 
-- ******* ---- Linux-4.4.0-179-generic-x86_64-with-debian-stretch-sid 2020-05-31 23:22:57
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         celery_demo:0x7f49c185d5d0
- ** ---------- .> transport:   amqp://kfs:**@kfs.pydemia.org:5672//
- ** ---------- .> results:     rpc://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . celery_demo.tasks.add_longtime_job

[2020-05-31 23:22:57,927: INFO/MainProcess] Connected to amqp://kfs:**@kfs.pydemia.org:5672//
[2020-05-31 23:22:58,902: INFO/MainProcess] mingle: searching for neighbors
[2020-05-31 23:23:02,249: INFO/MainProcess] mingle: all alone
[2020-05-31 23:23:04,547: INFO/MainProcess] celery@pydemia-server ready.
```

Run this at the same time:
```sh
python -m celery_demo.run_tasks
```

