# Cert-Manager

<https://cert-manager.io/docs/installation/kubernetes/>

```bash
# If cert-manager < v0.14.3, you should create the namespace manually
$ kubectl create namespace cert-manager

# Install the CustomResourceDefinitions and cert-manager itself
# cert-manager >= v0.14.3, Kubernetes >= 1.15
$ curl -sL https://github.com/jetstack/cert-manager/releases/download/v0.14.3/cert-manager.yaml -O && kubectl apply --validate=false -f cert-manager.yaml

# cert-manager >= v0.14.3, Kubernetes < 1.15
$ curl -sL https://github.com/jetstack/cert-manager/releases/download/v0.14.3/cert-manager-legacy.yaml -O && kubectl apply --validate=false -f cert-manager-legacy.yaml

# cert-manager < v0.14.3
$ curl -sL https://github.com/jetstack/cert-manager/releases/download/v0.13.1/cert-manager.yaml -O && kubectl apply --validate=false -f cert-manager.yaml
```

> **Note**: If you’re using a Kubernetes version below `v1.15` you will need to install **the legacy version of the manifests**. This version does not have API version conversion and only supports `cert-manager.io/v1alpha2` API resources.

> **Note**: If you are running Kubernetes v1.15.4 or below, you will need to add the `--validate=false` flag to your kubectl apply command above else you will receive a validation error relating to the `x-kubernetes-preserve-unknown-fields` field in `cert-manager`’s `CustomResourceDefinition` resources. This is a benign error and occurs due to the way `kubectl` performs resource validation.

> **Note**: By default,`cert-manager` will be installed into the `cert-manager namespace`. It is possible to run `cert-manager` in a different namespace, although you will need to make modifications to the deployment manifests.

## In `GKE`:

```sh
$ kubectl create clusterrolebinding cluster-admin-binding \
    --clusterrole=cluster-admin \
    --user=$(gcloud config get-value core/account)
```

:bell:**Note**: When running on `GKE (Google Kubernetes Engine)`, you may encounter a ‘permission denied’ error when creating some of these resources. This is a nuance of the way `GKE` handles `RBAC` and `IAM` permissions, and as such you should ‘elevate’ your own privileges to that of a `‘cluster-admin’` before running the above command. If you have already run the above command, you should run them again after elevating your permissions:
