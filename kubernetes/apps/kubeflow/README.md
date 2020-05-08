# Kubeflow

Homepage: <https://www.kubeflow.org>
Github: <https://github.com/kubeflow/>

## Installation

Install on an existing GKE cluster(`dex` and `Istio`: for Multi-User).

---
### (Optional) Access `gcloud` with `SERVICE-ACCOUNT`, if needed

A general-purpose Kubernetes cluster;Kubeflow, KFServing, NVIDIA Runtime, etc.

**NOTE**: 
[Available GPU Type for Each *Zone*](https://cloud.google.com/compute/docs/gpus#gpus-list)
[Available GPU Type for Each *Region*](https://cloud.google.com/ai-platform/training/docs/regions#americas_1)


#### 1. Check which account you're using:
```sh
$ gcloud auth list
                      Credentialed Accounts
ACTIVE  ACCOUNT
        <A-account@gmail.com>
*       <B-account>
        <C-account@domain.com>
        ...

To set the active account, run:
    $ gcloud config set account `ACCOUNT`
```

##### 1-1. SET **USER** ACCOUNT if not:
```sh
$ gcloud config set account `<C-account@domain.com>`
Updated property [core/account].

# Check it again
$ gcloud auth list
                      Credentialed Accounts
ACTIVE  ACCOUNT
        <A-account@gmail.com>
        <B-account>
*       <C-account@domain.com>
        ...

To set the active account, run:
    $ gcloud config set account `ACCOUNT`
```

#### 2. Log in `gcloud` with a `service account`:

```sh
$ gcloud iam service-accounts keys create \
    <KEY-NAME>.json \
    --iam-account <SERVICE-ACCOUNT> && \
  gcloud auth activate-service-account \
    <SERVICE-ACCOUNT> \
    --project=<GCP-PROJECT-ID> \
    --key-file=<KEY-NAME>.json
```

> In my case:
> ```sh
> # yjkim-kbcluster:  yjkim-kube-admin-sa@ds-ai-platform.iam.> gserviceaccount.com
> $ gcloud iam service-accounts keys create \
>     kbc-sa-key.json \
>     --iam-account yjkim-kube-admin-sa@ds-ai-platform.iam.> gserviceaccount.com && \
>   gcloud auth activate-service-account \
>     yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com \
>     --project=ds-ai-platform \
>     --key-file=kbc-sa-key.json
> 
> # yjkim-kubeflow-gui: yjkim-kubeflow-gui-vm@ds-ai-platform.iam.> gserviceaccount.com
> $ gcloud iam service-accounts keys create \
>     kfc-sa-key.json \
>     --iam-account yjkim-kubeflow-gui-vm@ds-ai-platform.iam.> gserviceaccount.com && \
>   gcloud auth activate-service-account \
>     yjkim-kubeflow-gui-vm@ds-ai-platform.iam.gserviceaccount.com \
>     --project=ds-ai-platform \
>     --key-file=kfc-sa-key.json
> ```

Then, the output would be the following:
```sh
created key [xxxxxxxxxx] of type [json] as [keyname.json] for [<SERVICE-ACCOUNT>]
Activated service account credentials for: [<SERVICE-ACCOUNT>]
```

NOW, you can manage GKE cluster, not as an *USER*, but as an **SERVICE-ACCOUNT**.  

Show the `gcloud auth list` again:
```sh
$ gcloud auth list
                      Credentialed Accounts
ACTIVE  ACCOUNT
        <A-account@gmail.com>
        <B-account>
        <C-account@domain.com>
*       <SERVICE-ACCOUNT>
        ...

To set the active account, run:
    $ gcloud config set account `ACCOUNT`
```

#### 3. Access to the `kube-cluster`:
```sh
$ gcloud container clusters get-credentials \
  yjkim-kbcluster \
  --region us-central1 \
  --project ds-ai-platform

$ alias gcloud-kbc="gcloud container clusters get-credentials yjkim-kbcluster --region us-central1 --project ds-ai-platform"
$ alias gcloud-kfc="gcloud container clusters get-credentials yjkim-kubeflow-gui --region us-west1-b --project ds-ai-platform"

$ kubectl config current-context
```

---

### Install `kubeflow` on GKE

#### 1. Prepare `kubectl`

```sh
# For Example: curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.18.0/bin/linux/amd64/kubectl
$ curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && \
chmod +x ./kubectl && \
mkdir -p $HOME/.local/bin && \
mv ./kubectl $HOME/.local/bin/kubectl

# RUN if `$HOME/.local/bin` is not in $PATH:
echo '
export PATH="$HOME/.local/bin:${PATH}"
' | tee -a ~/.bashrc && \
source ~/.bashrc
```

### Prepare `kfctl`

Releases: <https://github.com/kubeflow/kfctl/releases>

* Untar `kfctl release`
```sh
$ curl -fsSL https://github.com/kubeflow/kfctl/releases/download/v1.0.2/kfctl_v1.0.2-0-ga476281_linux.tar.gz | tar -zxvf -
chmod +x ./kfctl && \
mkdir -p $HOME/.local/bin && \
mv ./kfctl $HOME/.local/bin/kfctl

# RUN if `$HOME/.local/bin` is not in $PATH:
echo '
export PATH="$HOME/.local/bin:${PATH}"
' | tee -a ~/.bashrc 
source ~/.bashrc
```

* Create env_vars for deployment
```sh
# Add kfctl to PATH, to make the kfctl binary easier to use.
# Use only alphanumeric characters or - in the directory name.
export PATH="$HOME/bin:${PATH}"

# Set the following kfctl configuration file:
export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_istio_dex.v1.0.2.yaml"

# Set KF_NAME to the name of your Kubeflow deployment. You also use this
# value as directory name when creating your configuration directory.
# For example, your deployment name can be 'my-kubeflow' or 'kf-test'.
#export KF_NAME=<your choice of name for the Kubeflow deployment>
export KF_NAME="kubeflow"

# Set the path to the base directory where you want to store one or more 
# Kubeflow deployments. For example, /opt.
# Then set the Kubeflow application directory for this deployment.
#export BASE_DIR="/opt"
export BASE_DIR="${HOME}/opt"
export KF_DIR=${BASE_DIR}/${KF_NAME}
```

```sh
mkdir -p ${KF_DIR}
cd ${KF_DIR}

# Download the config file and change the default login credentials.
wget -O kfctl_istio_dex.yaml $CONFIG_URI
export CONFIG_FILE=${KF_DIR}/kfctl_istio_dex.yaml

# Credentials for the default user are admin@kubeflow.org:12341234
# To change them, please edit the dex-auth application parameters
# inside the KfDef file.
#vim $CONFIG_FILE

kfctl apply -V -f ${CONFIG_FILE}
```

```sh
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

Access it:
```
http://localhost:8080
```


---
## KF Serving

```sh
TAG=0.2.2 && \
wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
    -O "kfserving-${TAG}.yaml"
kubectl apply -f "kfserving-${TAG}.yaml"

TAG=v0.3.0 && \
wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
    -O "kfserving-${TAG}.yaml"
kubectl apply -f "kfserving-${TAG}.yaml"
```


## Sidecar Injection:
1. <https://cloud.google.com/istio/docs/istio-on-gke/installing#enabling_sidecar_injection>
2. https://istio.io/docs/setup/additional-setup/sidecar-injection/


## Expose `kubeflow`

<https://www.kubeflow.org/docs/started/k8s/kfctl-istio-dex/#expose-kubeflow>

* Old:
```yaml
# Please edit the object below. Lines beginning with a '#' will be ignored,
# and an empty file will abort the edit. If an error occurs while saving this file will be
# reopened with the relevant failures.
#
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"networking.istio.io/v1alpha3","kind":"Gateway","metadata":{"annotations":{},"name":"kubeflow-gateway","namespace":"kubeflow"},"spec":{"selector":{"istio":"ingressgateway"},"servers":[{"hosts":["*"],"port":{"name":"http","number":80,"protocol":"HTTP"}}]}}
  creationTimestamp: "2020-05-06T06:15:59Z"
  generation: 1
  name: kubeflow-gateway
  namespace: kubeflow
  resourceVersion: "301658"
  selfLink: /apis/networking.istio.io/v1alpha3/namespaces/kubeflow/gateways/kubeflow-gateway
  uid: 218a427f-68d1-434c-b404-9da2c294be9d
spec:
  selector:
    istio: ingressgateway
  servers:
  - hosts:
    - '*'
    port:
      name: http
      number: 80
      protocol: HTTP
```

* New `kubeflow-gateway-for-expose.yaml`:
```sh
kubectl apply -f kubeflow-gateway-for-expose.yaml
```

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"networking.istio.io/v1alpha3","kind":"Gateway","metadata":{"annotations":{},"name":"kubeflow-gateway","namespace":"kubeflow"},"spec":{"selector":{"istio":"ingressgateway"},"servers":[{"hosts":["*"],"port":{"name":"http","number":80,"protocol":"HTTP"}}]}}
  creationTimestamp: "2020-05-06T06:15:59Z"
  generation: 1
  name: kubeflow-gateway
  namespace: kubeflow
  resourceVersion: "301658"
  selfLink: /apis/networking.istio.io/v1alpha3/namespaces/kubeflow/gateways/kubeflow-gateway
  uid: 218a427f-68d1-434c-b404-9da2c294be9d
spec:
  selector:
    istio: ingressgateway
  servers:
  - hosts:
    - '*'
    port:
      name: http
      number: 80
      protocol: HTTP
    # Upgrade HTTP to HTTPS
    tls:
      httpsRedirect: true
  - hosts:
    - '*'
    port:
      name: https
      number: 443
      protocol: HTTPS
    tls:
      mode: SIMPLE
      privateKey: /etc/istio/ingressgateway-certs/tls.key
      serverCertificate: /etc/istio/ingressgateway-certs/tls.crt
```


## Expose with a LoadBalancer

**NOTE**: Check the GKE Add-ons `HTTP load balancing: Enabled`.

```sh
$ kubectl patch service -n istio-system istio-ingressgateway -p '{"spec": {"type": "LoadBalancer"}}'
$ kubectl get svc -n istio-system istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0]}'
```

## Create a certificate with `cert-manager`:

```yaml
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: istio-ingressgateway-certs
  namespace: istio-system
spec:
  commonName: istio-ingressgateway.istio-system.svc
  # Use ipAddresses if your LoadBalancer issues an IP
  ipAddresses:
  - "35.226.255.17"
  # Use dnsNames if your LoadBalancer issues a hostname (eg on AWS)
  dnsNames:
  - <LoadBalancer HostName>
  isCA: true
  issuerRef:
    kind: ClusterIssuer
    name: kubeflow-self-signing-issuer
  secretName: istio-ingressgateway-certs
```

After applying the above Certificate, `cert-manager` will generate the `TLS certificate` inside the `istio-ingressgateway-certs` secrets. The `istio-ingressgateway-certs secret` is mounted on the `istio-ingressgateway` deployment and used to serve `HTTPS`.

Navigate to `https://<LoadBalancer Address>/` and start using Kubeflow.