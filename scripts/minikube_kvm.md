# Minikube & KVM

## Installation

### KVM

```sh
sudo apt install qemu-kvm libvirt-bin bridge-utils ubuntu-vm-builder -y
sudo apt install libvirt-clients libvirt-daemon-system qemu-kvm -y
sudo yum install libvirt-daemon-kvm qemu-kvm -y

# GUI manager
sudo apt install virt-manager -y

# Authentication
sudo adduser $(id -un) libvirt
sudo adduser $(id -un) kvm
sudo adduser $(id -un) libvirtd
```

### Minikube

```sh
sudo wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 -O  /usr/local/bin/minikube
sudo chmod +x /usr/local/bin/minikube
```

### Docker Machine KVM driver

```sh
curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
chmod +x docker-machine-driver-kvm2
sudo mv docker-machine-driver-kvm2 /usr/local/bin/
```


```sh
(base)  pydemia@pydemia-xps-ubuntu  ~
❯ minikube start --vm-driver kvm2
😄  minikube v1.2.0 on linux (amd64)
🔥  Creating kvm2 VM (CPUs=2, Memory=2048MB, Disk=20000MB) ...
🐳  Configuring environment for Kubernetes v1.15.0 on Docker 18.09.6
💾  Downloading kubeadm v1.15.0
💾  Downloading kubelet v1.15.0
🚜  Pulling images ...
🚀  Launching Kubernetes ... 
⌛  Verifying: apiserver proxy etcd scheduler controller dns
🏄  Done! kubectl is now configured to use "minikube"
```

## Basics

```sh
❯ sudo virsh list
 Id    Name                           State
----------------------------------------------------
 1     minikube                       running

❯ kubectl cluster-info
Kubernetes master is running at https://192.168.39.118:8443
KubeDNS is running at https://192.168.39.118:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.

❯ kubectl config view

apiVersion: v1
clusters:
- cluster:
    certificate-authority: /home/pydemia/.minikube/ca.crt
    server: https://192.168.39.118:8443
  name: minikube
contexts:
- context:
    cluster: minikube
    user: minikube
  name: minikube
current-context: minikube
kind: Config
preferences: {}
users:
- name: minikube
  user:
    client-certificate: /home/pydemia/.minikube/client.crt
    client-key: /home/pydemia/.minikube/client.key

❯ kubectl get nodes
NAME       STATUS   ROLES    AGE     VERSION
minikube   Ready    master   7m15s   v1.15.0

❯ minikube ssh
                         _             _            
            _         _ ( )           ( )           
  ___ ___  (_)  ___  (_)| |/')  _   _ | |_      __  
/' _ ` _ `\| |/' _ `\| || , <  ( ) ( )| '_`\  /'__`\
| ( ) ( ) || || ( ) || || |\`\ | (_) || |_) )(  ___/
(_) (_) (_)(_)(_) (_)(_)(_) (_)`\___/'(_,__/'`\____)

$ pwd
/home/docker
$ 

```
