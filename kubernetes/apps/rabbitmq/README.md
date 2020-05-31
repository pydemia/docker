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

