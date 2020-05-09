# Calico

Cluster Networking via `calico`(used by Google)
**_CIDR Problem_ exists!_** *You should use `--pot-network-cidr=192.168.x.x/x` for `calico`!*

`192.168.0.0/16` -> `192.168.99.0/24`

> ```diff
> \- name: CALICO_IPV4POOL_CIDR
> ---  value: "192.168.0.0/16"
> +++  value: "192.168.99.0/24"
> ```

```bash
wget https://docs.projectcalico.org/v3.9/manifests/calico.yaml -O calico.yaml
sed -i -e 's?192.168.0.0/16?192.168.99.0/24?g' calico.yaml
kubectl apply -f calico.yaml
```

Messages:
```ascii
configmap/calico-config created
customresourcedefinition.apiextensions.k8s.io/felixconfigurations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamblocks.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/blockaffinities.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamhandles.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamconfigs.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/bgppeers.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/bgpconfigurations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ippools.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/hostendpoints.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/clusterinformations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/globalnetworkpolicies.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/globalnetworksets.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/networkpolicies.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/networksets.crd.projectcalico.org created
clusterrole.rbac.authorization.k8s.io/calico-kube-controllers created
clusterrolebinding.rbac.authorization.k8s.io/calico-kube-controllers created
clusterrole.rbac.authorization.k8s.io/calico-node created
clusterrolebinding.rbac.authorization.k8s.io/calico-node created
daemonset.apps/calico-node created
serviceaccount/calico-node created
deployment.apps/calico-kube-controllers created
serviceaccount/calico-kube-controllers created
```

#### `calicoctl` application as a pod:

In this article, `calicoctl version: v3.13.3` for now.
`docker pull calico/ctl:v3.13.3`

  - `etcd`
    ```sh
    kubectl apply -f https://docs.projectcalico.org/manifests/calicoctl-etcd.yaml
    ```

  - Kubernetes API datastore
    ```sh
     kubectl apply -f https://docs.projectcalico.org/manifests/calicoctl.yaml
    ```

You can then run commands using kubectl as shown below.
```sh
#kubectl exec -ti -n kube-system calicoctl -- /calicoctl get profiles -o wide
```

Create an `alias` as a command:
```sh
alias calicoctl="kubectl exec -i -n kube-system calicoctl /calicoctl -- "
```

```sh
echo '
alias calicoctl="kubectl exec -i -n kube-system calicoctl /calicoctl -- "
' | sudo tee -a /etc/bash.bashrc && \
source /etc/bash.bashrc && source ~/.bashrc
```


From [install-calicoctl-as-a-kube-pod](https://docs.projectcalico.org/getting-started/calicoctl/install#installing-calicoctl-as-a-kubernetes-pod)
