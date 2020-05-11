# Istio

## Install `istioctl`

```sh
$ curl -fsSL https://github.com/istio/istio/releases/download/1.5.2/istioctl-1.5.2-linux.tar.gz | tar -zxvf -
$ mkdir -p $HOME/.local/bin && \
  mv istioctl $HOME/.local/bin/
```

or 

```sh
curl -sL https://istio.io/downloadIstioctl | ISTIO_VERSION=1.4.1 sh - &&\
  mkdir -p $HOME/.local/bin && \
  cp $HOME/.istioctl/bin/istioctl $HOME/.local/bin/
```

Get an overview of your mesh:
```sh
$ istioctl proxy-status
```

## Install `Istio`

```sh
curl -sL https://istio.io/downloadIstio | ISTIO_VERSION=1.3.1 sh -
```

> **From KFServing**: from Kubeflow 1.0 onwards, KNative 0.11.1 and Istio 1.1.6 are installed by default. If you are using DEX based config for Kubeflow 1.0, `Istio 1.3.1` is installed by default in your Kubeflow cluster. To summarize, we would recommend KNative 0.11.1 at a minimum for KFServing 0.3.0 and for the KFServing code in master. For Istio use versions 1.1.6 and 1.3.1 which have been tested, and for Kubernetes use 1.15+

### **For private GKE clusters:** up `15017` port
An automatically created firewall rule does not open port `15017`. This is needed by the Pilot discovery validation webhook.

To review this firewall rule for master access:
```sh
$ gcloud compute firewall-rules list --filter="name~gke-<cluster-name>-[0-9a-z]*-master"
```
To replace the existing rule and allow master access:
```sh
$ gcloud compute firewall-rules update <firewall-rule-name> --allow tcp:10250,tcp:443,tcp:15017
```

Grant cluster administrator (admin) permissions to the current user. To create the necessary `RBAC` rules for `Istio`, the current user requires admin permissions.(Same as `cert-manager`)
```sh
$ kubectl create clusterrolebinding cluster-admin-binding \
    --clusterrole=cluster-admin \
    --user=$(gcloud config get-value core/account)
```
