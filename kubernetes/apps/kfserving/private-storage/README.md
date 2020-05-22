
# Set Private


## Docker Hub

```sh
$ docker login
Authenticating with existing credentials...
WARNING! Your password will be stored unencrypted in xxxxx/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded

$ cat xxxxx/config.json |grep "https://index.docker.io/v1/"

"https://index.docker.io/v1/": {
                        "auth": "xxxxxxxxxxxxx"
                },

$ kubectl create secret generic regcred \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson

# $ kubectl create secret docker-registry regcred \
#     --docker-server=docker.io \
#     --docker-username=<your-name> \
#     --docker-password=<your-pword> \
#     --docker-email=<your-email>

$ kubectl create secret docker-registry docker-secret-key \
    --docker-server=docker.io \
    --docker-username=pydemia \
    --docker-password=<password> \
    --docker-email=pydemia@gmail.com
```


```sh
$ kubectl create secret docker-registry \
   gcr-private-key \
    --docker-server=docker.io \
    --docker-username=_json_key \
    --docker-password="$(cat ./gcloud-application-credentials.json)" \
    --docker-email=yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com
```

## GCP

```sh
$ gcloud iam service-accounts keys create gcloud-application-credentials.json \
    --iam-account yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com
```

```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: gcs-private-sa
  namespace: inference-test
EOF
#serviceaccount/gcs-private-sa created
```

```sh
# $ kubectl create secret generic gcs-private-key \
#     --from-file=gcloud-application-credentials.json=xxxx-4129b72eaa4a.json
# secret/gcs-private-sa created

$ kubectl -n inference-test create secret generic gcs-private-key \
    --from-file=gcloud-application-credentials.json=xxxx-4129b72eaa4a.json
secret/gcs-private-sa created
```


```sh
# $ kubectl create secret docker-registry \
#    gcr-private-key \
#     --docker-server=gcr.io \
#     --docker-username=_json_key \
#     --docker-password="$(cat ./gcloud-application-credentials.json)" \
#     --docker-email=yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com
# secret/gcr-private-key created

$ kubectl -n inference-test create secret docker-registry \
   gcr-private-key \
    --docker-server=gcr.io \
    --docker-username=_json_key \
    --docker-password="$(cat ./gcloud-application-credentials.json)" \
    --docker-email=yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com
secret/gcr-private-key created
```

```sh
# $ kubectl patch sa default \
#     -p '{"imagePullSecrets": [{"name": "gcr-private-key"}]}'
# serviceaccount/default patched

$ kubectl -n inference-test patch sa gcs-private-sa \
    -p '{"imagePullSecrets": [{"name": "gcr-private-key"}]}'
serviceaccount/gcs-private-sa patched

$ kubectl -n inference-test patch sa gcs-private-sa \
    -p '{"secrets": [{"name": "gcs-private-key"},{"name": "gcs-private-sa-token-qhx6w"}],"imagePullSecrets": [{"name": "gcr-private-key"}]}'
# kubectl -n inference-test patch sa default \
# -p '{"imagePullSecrets": [{"name": "yjkim-kube-admin-sa-gcr-private-key"}]}'
# kubectl -n kfserving-system patch sa default \
# -p '{"imagePullSecrets": [{"name": "yjkim-kube-admin-sa-gcr-private-key"}]}'
```

```sh
$ kubectl -n inference-test describe sa gcs-private-sa
```

```sh
$ kubectl -n inference-test describe sa gcs-private-sa
Name:                gcs-private-sa
Namespace:           inference-test
Labels:              <none>
Annotations:         Image pull secrets:  gcr-private-key
Mountable secrets:   gcs-private-sa-token-g2n79
Tokens:              gcs-private-sa-token-g2n79
Events:              <none>

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
  namespace: default
items:

  imagePullSecrets:
  - name: yjkim-kube-admin-sa-gcr-private-key


apiVersion: v1
kind: ServiceAccount
metadata:
  name: yjkim-kube-admin-sa-gcr
  namespace: 
secrets:
  - name: yjkim-kube-admin-sa-gcr-private-key
imagePullSecrets:
  - name: yjkim-kube-admin-sa-gcr-private-key
```

---


## AWS

<https://github.com/kubeflow/kfserving/tree/master/docs/samples/s3>
<https://www.kubeflow.org/docs/aws/aws-e2e/>

`s3-private-key.yaml`
```sh
apiVersion: v1
kind: Secret
metadata:
  name: s3-private-key
  namespace: inference-test
  annotations:
     serving.kubeflow.org/s3-endpoint: 946648250772.s3-control.us-east-2.amazonaws.com # replace with your s3 endpoint
     serving.kubeflow.org/s3-usehttps: "0" # by default 1, for testing with minio you need to set to 0
type: Opaque
data:
  awsAccessKeyID: xxxxxxxxxx
  awsSecretAccessKey: xxxxxxxxx

```

`s3-private-sa.yaml`
```sh
apiVersion: v1
kind: ServiceAccount
metadata:
  name: s3-private-sa
  namespace: inference-test
secrets:
- name: s3-private-key
```

```sh
$ kubectl -n inference-test patch sa s3-private-sa \
    -p '{"imagePullSecrets": [{"name": "docker-secret-key"}]}'
```

Then,

`s3-private-sa.yaml`
```sh
apiVersion: v1
kind: ServiceAccount
metadata:
  name: s3-private-sa
  namespace: inference-test
secrets:
- name: s3-private-key
imagePullSecrets:
- name: docker-secret-key
```