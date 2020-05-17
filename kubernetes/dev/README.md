# Dev

## Tools

* `go`
* `dep`
* `ko`
* `kubectl`
* `kustomize`

### `go`

`go >= 1.13.0`

```sh
curl -sS https://dl.google.com/go/go1.14.3.linux-amd64.tar.gz -O

# For all users
tar -C /usr/local -xzf go1.14.3.linux-amd64.tar.gz
export GO_HOME="/usr/local/go"
export PATH="${GO_HOME}/bin:${PATH}"

##### $GOPATH must not be set to $GOROOT
export GOPATH="${HOME}/.gopath"  # ${HOME}/go
export GOROOT="${GO_HOME}"

# For a single user
mkdir -p $HOME/.local
tar -C $HOME/.local -xzf go1.14.3.linux-amd64.tar.gz
export GO_HOME="${HOME}/.local/go"
export PATH="${GO_HOME}/bin:${PATH}"
##### $GOPATH must not be set to $GOROOT
export GOPATH="${HOME}/.gopath"  # ${HOME}/go
export GOROOT="${GO_HOME}"
```

### `dep`

<https://github.com/golang/dep>

```sh
$ sudo apt-get install go-dep
```

or 

```sh
$ curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  5230  100  5230    0     0  10717      0 --:--:-- --:--:-- --:--:-- 10717
ARCH = amd64
OS = linux
Will install into /home/pydemia/.gopath/bin
Fetching https://github.com/golang/dep/releases/latest..
Release Tag = v0.5.4
Fetching https://github.com/golang/dep/releases/tag/v0.5.4..
Fetching https://github.com/golang/dep/releases/download/v0.5.4/dep-linux-amd64..
Setting executable permissions.
Moving executable to /home/pydemia/.gopath/bin/dep
```

### `ko`

<https://github.com/google/ko>

```sh
$ GO111MODULE=on go get github.com/google/ko/cmd/ko
go: downloading github.com/google/ko v0.5.1
go: found github.com/google/ko/cmd/ko in github.com/google/ko v0.5.1
go: downloading github.com/spf13/cobra v0.0.5
...

```

### `kustomize`

`kustomize >= v3.5.4`
<https://github.com/kubernetes-sigs/kustomize/tree/v2.0.3>

```sh
$ curl -s "https://raw.githubusercontent.com/\
kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
mv kustomize $GO_HOME/bin/
```

or

```sh
$ GO111MODULE=on go get sigs.k8s.io/kustomize/kustomize/v3@v3.5.4

go: downloading sigs.k8s.io/kustomize/kustomize/v3 v3.5.4
go: downloading sigs.k8s.io/kustomize/cmd/config v0.0.5
go: downloading sigs.k8s.io/kustomize/api v0.3.2
go: downloading sigs.k8s.io/kustomize/kyaml v0.0.6
go: downloading github.com/googleapis/gnostic v0.0.0-20170729233727-0c5108395e2d
go: downloading golang.org/x/sys v0.0.0-20190922100055-0a153f010e69
go: downloading github.com/google/go-cmp v0.3.0
```

### Set envs

`KO_DOCKER_REPO`: The docker repository to which developer images should be pushed (e.g. `docker.io/<username>/[project]`).

```sh
#$ export KO_DOCKER_REPO=gcr.io/ds-ai-platform/microorganism
$ export KO_DOCKER_REPO=gcr.io/ds-ai-platform/microorganism
#$ export KO_DOCKER_REPO=docker.io/pydemia/microorganism
```

### Clone the repository

Clone `kfserving` repository to `${GOPATH}/src/github.com/kubeflow`

* fork `https://github.com/kubeflow/kfserving` first.
* clone and add `upstream` to original repo.

```sh
git clone -b v0.3.0 https://github.com/pydemia/kfserving ${GOPATH}/src/github.com/kubeflow
cd ${GOPATH}/src/github.com/kubeflow
git remote add upstream git@github.com:kubeflow/kfserving.git
git remote set-url --push upstream no_push
```

#### Create a custom image to deploy

* In case you don't use `cert-manager`:
```sh
export KFSERVING_ENABLE_SELF_SIGNED_CA=true
```

* use env
```sh
export KO_DOCKER_REPO=gcr.io/ds-ai-platform/microorganism
```

`ConfigMap: inferenceservice-config`
```yaml
"microorganism": {
  "image": "gcr.io/ds-ai-platform/microorganism",
  "defaultImageVersion": "v0.1.0-http",
  "allowedImageVersions": [
      "v0.1.0-http",
      "v0.1.0-http-gpu",
      "v0.1.0-http-grpc",
      "v0.1.0-http-grpc-gpu"
  ]
},
```

`deploy: microorganism.yaml`
```yaml
apiVersion: "serving.kubeflow.org/v1alpha2"
kind: "InferenceService"
metadata:
  name: "microorganism"
spec:
  default:
    predictor:
      microorganism:
        storageUri: "gs://brain-ds/microorganism_13/model"
```


```sh
$ kubectl -n inference-test apply -f microorganism.yaml
```