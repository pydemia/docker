# Kubernetes

## Installation

```sh
sudo apt install kubelet kubeadm kubectl kubernetes-cni
```

```txt
apt-get update && apt-get install -y apt-transport-https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
apt-get update
apt-get install -y kubelet kubeadm kubectl kubernetes-cni
apt-mark hold kubelet kubeadm kubectl kubernetes-cni
```

## Port Setting

Control-plane node(s):

| Protocol | Direction | Port | Range | Purpose	Used By
TCP	Inbound	6443*	Kubernetes API server	All
TCP	Inbound	2379-2380	etcd server client API	kube-apiserver, etcd
TCP	Inbound	10250	Kubelet API	Self, Control plane
TCP	Inbound	10251	kube-scheduler	Self
TCP	Inbound	10252	kube-controller-manager	Self
```sh
sudo ufw allow 6443/tcp
sudo ufw allow 2379-2380/tcp
sudo ufw allow 10250/tcp
sudo ufw allow 10251/tcp
sudo ufw allow 10252/tcp
```

Worker node(s):

Protocol	Direction	Port Range	Purpose	Used By
TCP	Inbound	10250	Kubelet API	Self, Control plane
TCP	Inbound	30000-32767	NodePort Services**	All
```sh
sudo ufw allow 10250/tcp
sudo ufw allow 30000-32767/tcp
```

## Daemon Setting

```sh
systemctl daemon-reload
systemctl restart kubelet
```
