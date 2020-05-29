```sh
$ kubectl logs -n knative-serving activator-8cb6d456-6kzwh activator
2020/05/26 07:33:50 Failed to get k8s version Get https://10.187.0.1:443/version?timeout=32s: dial tcp 10.187.0.1:443: connect: connection refused
2020/05/26 07:33:51 Failed to get k8s version Get https://10.187.0.1:443/version?timeout=32s: dial tcp 10.187.0.1:443: connect: connection refused
2020/05/26 07:33:52 Failed to get k8s version Get https://10.187.0.1:443/version?timeout=32s: dial tcp 10.187.0.1:443: connect: connection refused
2020/05/26 07:33:53 Failed to get k8s version Get https://10.187.0.1:443/version?timeout=32s: dial tcp 10.187.0.1:443: connect: connection refused
2020/05/26 07:33:54 Failed to get k8s version Get https://10.187.0.1:443/version?timeout=32s: dial tcp 10.187.0.1:443: connect: connection refused
2020/05/26 07:33:55 Failed to get k8s version Get https://10.187.0.1:443/version?timeout=32s: dial tcp 10.187.0.1:443: connect: connection refused
2020/05/26 07:33:56 Failed to get k8s version Get https://10.187.0.1:443/version?timeout=32s: dial tcp 10.187.0.1:443: connect: connection refused
2020/05/26 07:33:57 Failed to get k8s version Get https://10.187.0.1:443/version?timeout=32s: dial tcp 10.187.0.1:443: connect: connection refused
...
```

```sh
kubectl get svc --all-namespaces |grep 10.187.0.1
NAMESPACE     NAME          TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
default       kubernetes    ClusterIP      10.187.0.1      <none>        443/TCP             13d
kube-system   kube-dns      ClusterIP      10.187.0.10     <none>        53/UDP,53/TCP       13d
```