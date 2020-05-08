# Kubeflow

Homepage: <https://www.kubeflow.org>
Github: <https://github.com/kubeflow/>

## Installation

### Prepare `kubectl`

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

### Prepare `gcloud` Setting

Log in `gcloud` and create a credential

> **WARNING**: `gcloud auth login` no longer writes application default credentials.
> If you need to use ADC, see:
>   `gcloud auth application-default --help`

#### Create a Service Account for `kubeflow`
```sh
# Create a sa
$ gcloud iam service-accounts create gcpcmdlineuser --display-name "GCP Service Account"
# List users
$ gcloud iam service-accounts list --filter yjkim
# Download the sa key
$ gcloud iam service-accounts keys create gcpcmdlineuser.json --iam-account gcpcmdlineuser@someproject.iam.gserviceaccount.com
# Associate a ROLE
$ gcloud iam roles create <ROLE NAME> --project <YOUR PROJECT ID> --file ./rolename.yaml
$ gcloud projects add-iam-policy-binding <PROJECT ID> --role <ROLE NAME> --member serviceAccount:<EMAIL ADDRESS>
#$ gcloud projects add-iam-policy-binding someprojecthere --member "serviceAccount:gcpcmdlineuser@someproject.iam.gserviceaccount.com" --role "roles/owner"
# Activate the sa
$ gcloud auth activate-service-account --project=someproject --key-file=gcpcmdlineuser.json
```

#### List Users
```sh
export KF_SA_NAME="yjkim-kube-admin-sa"
export KF_PJT="ds-ai-platform"
export KF_SA="${KF_SA_NAME}@${KF_PJT}.iam.gserviceaccount.com"
echo "${KF_SA_NAME}_key.json"
gcloud iam service-accounts keys create "${KF_SA_NAME}_key.json" --iam-account="${KF_SA}"
gcloud auth activate-service-account --project="${KF_PJT}" --key-file="${KF_SA_NAME}_key.json"

gcloud config set account "${KF_SA}"
gcloud auth application-default login --no-launch-browser
gcloud auth application-default login \
    --client-id-file="${KF_SA_NAME}_key.json"

```

```sh
$ gcloud auth login
```

Log in with a credential:
```sh
# If you need to create a credential to login:
$ gcloud auth application-default login

# If you'd like to login by passing in a file containing your own client id:
$ gcloud auth application-default login \
    --client-id-file=clientid.json
```

[JSON Format](https://github.com/googleapis/google-api-python-client/blob/8496ebe7e4c282371c831cabdeb390855ff0d270/docs/client-secrets.md)

```json
{
  "client_id": "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com",
  "client_secret": "d-FL95Q19q7MQmFpd7hHD0Ty",
  "refresh_token": "1//0eYgbGnATW3A6CgYIARAAGA4SNwF-L9Ir3ogjmNx3Y5rRMFz-ptfy_EOkrg7co7QmY7t_6VtTIg1M3BRgZF79G8ZnQLndfQRQVNs",
  "type": "authorized_user"
}
{
  "installed": {
    "client_id": "asdfjasdljfasdkjf",
    "client_secret": "1912308409123890",
    "redirect_uris": ["https://www.example.com/oauth2callback"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

---
## Install on an existing cluster(`dex` and `Istio`: for Multi-User)


### Access `gcloud`

A general-purpose Kubernetes cluster;Kubeflow, KFServing, NVIDIA Runtime, etc.

**NOTE**: 
[Available GPU Type for Each *Zone*](https://cloud.google.com/compute/docs/gpus#gpus-list)
[Available GPU Type for Each *Region*](https://cloud.google.com/ai-platform/training/docs/regions#americas_1)


# GCP Kubernetes cluster:

```sh
$ gcloud container clusters get-credentials yjkim-kbcluster --region us-central1 --project ds-ai-platform

$ alias gcloud-kbc="gcloud container clusters get-credentials yjkim-kbcluster --region us-central1 --project ds-ai-platform"
$ alias gcloud-kfc="gcloud container clusters get-credentials yjkim-kubeflow-gui --region us-west1-b --project ds-ai-platform"

```

### Prepare `kfctl`

Releases: <https://github.com/kubeflow/kfctl/releases>

* Untar `kfctl release`
```sh
$ curl -fsSL https://github.com/kubeflow/kfctl/releases/download/v1.0.2/kfctl_v1.0.2-0-ga476281_linux.tar.gz | tar -zxvf -
./kfctl
mkdir -p $HOME/.local/bin
cp kfctl $HOME/.local/bin
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