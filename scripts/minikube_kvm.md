# Minikube & KVM

## Installation

### KVM

```sh
sudo apt install qemu-kvm libvirt-bin bridge-utils ubuntu-vm-builder -y

# GUI manager
sudo apt install virt-manager -y

# Authentication
sudo adduser $(id -un) libvirt
sudo adduser $(id -un) kvm

# sudo adduser $(id -un) libvirtd
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

## Authentication



## 
curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
