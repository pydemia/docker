# Istio


## Install `istioctl`

```sh
$ curl -fsSL https://github.com/istio/istio/releases/download/1.5.2/istioctl-1.5.2-linux.tar.gz | tar -zxvf -
$ mkdir -p $HOME/.local/bin && \
  mv istioctl $HOME/.local/bin/
```

or 

```sh
$ curl -sL https://istio.io/downloadIstioctl | sh -
 export PATH=$PATH:$HOME/.istioctl/bin
```

Get an overview of your mesh:
```sh
$ istioctl proxy-status
```