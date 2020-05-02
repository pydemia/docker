# Jetson Nano

## Set-up

### Boot-up

*Renew the source image: `nv-jetson-nano-sd-card-image-r32.4.2.img`

* [Get an Image(>= 4.2.1)](https://developer.nvidia.com/embedded/jetpack)
* [First Boot](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#write)

### Network Config

```sh
$ route

Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         _gateway        0.0.0.0         UG    100    0        0 eth0
link-local      0.0.0.0         255.255.0.0     U     1000   0        0 eth0
192.168.0.0     0.0.0.0         255.255.0.0     U     100    0        0 eth0

$ netstat -rn

Kernel IP routing table
Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
0.0.0.0         192.168.0.1     0.0.0.0         UG        0 0          0 eth0
169.254.0.0     0.0.0.0         255.255.0.0     U         0 0          0 eth0
192.168.0.0     0.0.0.0         255.255.0.0     U         0 0          0 eth0
```

#### Hostname

`/etc/hosts`
```sh
# Kubernetes cluster:
192.168.2.11   kube-jn00
192.168.2.12   kube-jn01
192.168.2.13   kube-jn02
192.168.2.14   kube-jn03
```

#### (Optional)`ssh-key`


`~/.ssh/config`
```sh
Host kb00
 HostName kube-jn00
 User pydemia
 IdentityFile ~/.ssh/pydemia-kubecluster-key

Host kb01
 HostName kube-jn01
 User pydemia
 IdentityFile ~/.ssh/pydemia-kubecluster-key

Host kb02
 HostName kube-jn02
 User pydemia
 IdentityFile ~/.ssh/pydemia-kubecluster-key

Host kb03
 HostName kube-jn03
 User pydemia
 IdentityFile ~/.ssh/pydemia-kubecluster-key
```


```sh
ssh-keygen -f pydemia-kubecluster-key
ssh-keygen -f pydemia-kubecluster-key.pub -m 'PEM' -e > pydemia-kubecluster-key.pem

ssh-copy-id -i ~/.ssh/pydemia-kubecluster-key.pub kube-jn00
ssh-copy-id -i ~/.ssh/pydemia-kubecluster-key.pub kube-jn01
ssh-copy-id -i ~/.ssh/pydemia-kubecluster-key.pub kube-jn02
ssh-copy-id -i ~/.ssh/pydemia-kubecluster-key.pub kube-jn03
```

which is equivalent:
```sh
cat ~/.ssh/pydemia-kubecluster-key.pub | ssh pydemia@192.168.2.11 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat > ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```


Just in case of re-establishing the authenticity of known-hosts:
```sh
ssh-keygen -f "/home/pydemia/.ssh/known_hosts" -R 192.168.2.11
ssh-keygen -f "/home/pydemia/.ssh/known_hosts" -R 192.168.2.12
ssh-keygen -f "/home/pydemia/.ssh/known_hosts" -R 192.168.2.13
ssh-keygen -f "/home/pydemia/.ssh/known_hosts" -R 192.168.2.14
```



### System Basic Setting

```sh
sudo apt update
sudo apt install -y \
  build-essential \
  vim htop \
  git tree curl \
  python3-pip

curl -sL https://deb.nodesource.com/setup_12.x  | sudo bash - && \
sudo apt-get -y install nodejs && \
sudo npm install -g npm

# Set Locale
sudo apt-get update -y && \
sudo apt-get install -y locales && \
sudo locale-gen --purge "en_US.UTF-8"
sudo bash -c "echo 'LC_ALL=en_US.UTF-8' >> /etc/environment"
sudo bash -c "echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen"
sudo bash -c "echo 'LANG=en_US.UTF-8' > /etc/locale.conf"
```

* Disable GUI

```sh
sudo systemctl set-default multi-user.target
#--------------------------------------------------#
#Removed /etc/systemd/system/default.target.
#Created symlink /etc/systemd/system/default.target → /lib/systemd/system/multi-user.target.

```

* High-Power mode(10W)
```sh
sudo nvpmodel -m 0
```

* Disable SWAP Memory (it can causes issues on k8s)

```sh
sudo mv /etc/systemd/nvzramconfig.sh /etc/systemd/nvzramconfig.sh.bak && sudo shutdown -r now


free -h
              total        used        free      shared  buff/cache   available
Mem:           3.9G        178M        3.4G         17M        284M        3.5G
Swap:            0B          0B          0B
```

(Optional) For `master`:
```sh
# GCLOUD
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && \
sudo apt-get update -y && \
sudo apt-get install google-cloud-sdk -y

# AWS CLI 2
curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
unzip -q awscliv2.zip && \
sudo ./aws/install && \
rm -rf ./aws && \
rm awscliv2.zip


# AZURE CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```


### Docker Setting

Check docker version:
`docker --version`

#### If `docker < 18.09`(which is not in `r32.4.2`):

```sh
sudo apt-get remove docker docker-engine docker.io containerd runc -y

sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common -y

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88

#sudo add-apt-repository \
#   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
#   $(lsb_release -cs) \
#   stable"

sudo add-apt-repository \
   "deb [arch=arm64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt update

sudo apt-get install -y \
  docker-ce=5:18.09.7~3-0~ubuntu-bionic \
  docker-ce-cli=5:18.09.7~3-0~ubuntu-bionic \
  containerd.io \
  --allow-downgrades

#sudo apt install docker-ce docker-ce-cli containerd.io -y

```


* Set a group `docker`   
Add current user to docker group to use docker command without sudo, following this guide: https://docs.docker.com/install/linux/linux-postinstall/. The required commands are following:
```sh
sudo groupadd docker # already exists in `r32.4.2`.
sudo usermod -aG docker $USER
newgrp docker  # to change the current group ID (GID) during a login session.
```

* Set the NVidia runtime as a default runtime in Docker.

Default:
```sh
cat /etc/docker/daemon.json
{
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

change it to:
```sh
sudo tee /etc/docker/daemon.json << EOF
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
    "exec-opts": ["native.cgroupdriver=systemd"],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m"
    },
    "storage-driver": "overlay2"
}

EOF
```

* <https://github.com/NVIDIA/nvidia-docker/wiki/Advanced-topics#default-runtime>
* <https://kubernetes.io/docs/setup/production-environment/#cgroup-drivers>
* <https://kubernetes.io/ko/docs/setup/production-environment/#cgroup-%EB%93%9C%EB%9D%BC%EC%9D%B4%EB%B2%84>

* Docker Storage Drivers (<https://docs.docker.com/storage/storagedriver/select-storage-driver/>)
| Union File System(Technology) | Storage driver name |
| :---------------------------- | :------------------ |
| OverlayFS	| `overlay` or `overlay2` |
| AUFS	| `aufs` |
| Btrfs	| `btrfs` |
| Device Mapper	| `devicemapper` |
| VFS	| `vfs` |
| ZFS	| `zfs` |


> By changing the default runtime,
> you are sure that every Docker command and every Docker-based tool will be **_allowed to access the GPU_**.

* Set NVIDIA
```sh
ls /usr/local |grep cuda
#----------#
lrwxrwxrwx  1 root root    9 Apr 19 11:57 cuda -> cuda-10.2
drwxr-xr-x 12 root root 4096 Apr 19 11:57 cuda-10.2
```

Set ENV in `/etc/bash.bashrc` & `/etc/profile`

```sh
echo '
# CUDA PATH
export CUDA_HOME="/usr/local/cuda-10.2" # cuda -> cuda-10.2
export PATH="${CUDA_HOME}/bin${PATH:+:${PATH}}"
export LD_LIBRARY_PATH="${CUDA_HOME}/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
export LD_LIBRARY_PATH="${CUDA_HOME}/include${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:+${LD_LIBRARY_PATH}:}${CUDA_HOME}/extras/CUPTI/lib64"
' | sudo tee -a /etc/bash.bashrc > /dev/null

echo '
# CUDA PATH
export CUDA_HOME="/usr/local/cuda-10.2" # cuda -> cuda-10.2
export PATH="${CUDA_HOME}/bin${PATH:+:${PATH}}"
export LD_LIBRARY_PATH="${CUDA_HOME}/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
export LD_LIBRARY_PATH="${CUDA_HOME}/include${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:+${LD_LIBRARY_PATH}:}${CUDA_HOME}/extras/CUPTI/lib64"
' | sudo tee -a /etc/profile > /dev/null

```

* Check NVIDIA Settings

```sh
sudo dpkg --get-selections | grep nvidia
#-------------------------------------------#
libnvidia-container-tools                       install
libnvidia-container0:arm64                      install
nvidia-container-csv-cuda                       install
nvidia-container-csv-cudnn                      install
nvidia-container-csv-tensorrt                   install
nvidia-container-csv-visionworks                install
nvidia-container-runtime                        install
nvidia-container-toolkit                        install
nvidia-docker2                                  install
nvidia-l4t-3d-core                              install
nvidia-l4t-apt-source                           install
nvidia-l4t-bootloader                           install
nvidia-l4t-camera                               install
nvidia-l4t-configs                              install
nvidia-l4t-core                                 install
nvidia-l4t-cuda                                 install
nvidia-l4t-firmware                             install
nvidia-l4t-graphics-demos                       install
nvidia-l4t-gstreamer                            install
nvidia-l4t-init                                 install
nvidia-l4t-initrd                               install
nvidia-l4t-jetson-io                            install
nvidia-l4t-jetson-multimedia-api                install
nvidia-l4t-kernel                               install
nvidia-l4t-kernel-dtbs                          install
nvidia-l4t-kernel-headers                       install
nvidia-l4t-multimedia                           install
nvidia-l4t-multimedia-utils                     install
nvidia-l4t-oem-config                           install
nvidia-l4t-tools                                install
nvidia-l4t-wayland                              install
nvidia-l4t-weston                               install
nvidia-l4t-x11                                  install
nvidia-l4t-xusb-firmware                        install
```

```sh
sudo docker info | grep nvidia
#-----------------------------#
Runtimes: nvidia runc
```


* Reboot
```sh
sudo shutdown -r now
```

### Test Docker GPU support

<https://ngc.nvidia.com/catalog/containers>
Base: `docker pull nvcr.io/nvidia/l4t-base:r32.4.2`
ML: `docker pull nvcr.io/nvidia/l4t-ml:r32.4.2-py3`
Tensorflow: `docker pull nvcr.io/nvidia/l4t-tensorflow:r32.4.2-tf1.15-py3`
PyTorch: `docker pull nvcr.io/nvidia/l4t-pytorch:r32.4.2-pth1.5-py3`

* Building CUDA in Containers on Jetson (Master)
Change base_image: `FROM nvcr.io/nvidia/l4t-base:r32.4 -> FROM nvcr.io/nvidia/l4t-base:r32.4.2

```sh
cd ~
mkdir /tmp/docker-build && cd /tmp/docker-build
cp -r /usr/local/cuda/samples/ ./
tee ./Dockerfile <<EOF
FROM nvcr.io/nvidia/l4t-base:r32.4.2

RUN apt-get update && apt-get install -y --no-install-recommends make g++
COPY ./samples /tmp/samples

WORKDIR /tmp/samples/1_Utilities/deviceQuery
RUN make clean && make

CMD ["./deviceQuery"]
EOF

docker build . -t pydemia/nvidia-jn-devicequery:r32.4.2

```

* Push it
```sh
docker login
docker push pydemia/nvidia-jn-devicequery:r32.4.2
```

* Run it
Test a Docker image
we are ready to test if Docker runs correctly and supports GPU.
To make this easier, we created a dedicated Docker image with “deviceQuery” tool from the CUDA SDK which is used to query the GPU and present its capabilities. The command to run it is simple:
```diff
-docker run --rm -it --runtime nvidia pydemia/nvidia-jn-devicequery:r32.4.2 ./deviceQuery
+docker run --rm -it --runtime nvidia pydemia/nvidia-jn-devicequery:r32.4.2
```

Then, The output is the following:
```ascii
./deviceQuery Starting...

 CUDA Device Query (Runtime API) version (CUDART static linking)

Detected 1 CUDA Capable device(s)

Device 0: "NVIDIA Tegra X1"
  CUDA Driver Version / Runtime Version          10.2 / 10.2
  CUDA Capability Major/Minor version number:    5.3
  Total amount of global memory:                 3964 MBytes (4156837888 bytes)
  ( 1) Multiprocessors, (128) CUDA Cores/MP:     128 CUDA Cores
  GPU Max Clock rate:                            922 MHz (0.92 GHz)
  Memory Clock rate:                             13 Mhz
  Memory Bus Width:                              64-bit
  L2 Cache Size:                                 262144 bytes
  Maximum Texture Dimension Size (x,y,z)         1D=(65536), 2D=(65536, 65536), 3D=(4096, 4096, 4096)
  Maximum Layered 1D Texture Size, (num) layers  1D=(16384), 2048 layers
  Maximum Layered 2D Texture Size, (num) layers  2D=(16384, 16384), 2048 layers
  Total amount of constant memory:               65536 bytes
  Total amount of shared memory per block:       49152 bytes
  Total number of registers available per block: 32768
  Warp size:                                     32
  Maximum number of threads per multiprocessor:  2048
  Maximum number of threads per block:           1024
  Max dimension size of a thread block (x,y,z): (1024, 1024, 64)
  Max dimension size of a grid size    (x,y,z): (2147483647, 65535, 65535)
  Maximum memory pitch:                          2147483647 bytes
  Texture alignment:                             512 bytes
  Concurrent copy and kernel execution:          Yes with 1 copy engine(s)
  Run time limit on kernels:                     Yes
  Integrated GPU sharing Host Memory:            Yes
  Support host page-locked memory mapping:       Yes
  Alignment requirement for Surfaces:            Yes
  Device has ECC support:                        Disabled
  Device supports Unified Addressing (UVA):      Yes
  Device supports Compute Preemption:            No
  Supports Cooperative Kernel Launch:            No
  Supports MultiDevice Co-op Kernel Launch:      No
  Device PCI Domain ID / Bus ID / location ID:   0 / 0 / 0
  Compute Mode:
     < Default (multiple host threads can use ::cudaSetDevice() with device simultaneously) >

deviceQuery, CUDA Driver = CUDART, CUDA Driver Version = 10.2, CUDA Runtime Version = 10.2, NumDevs = 1
Result = PASS
```


### Kubernetes Setting


* Static IP addressing  
```sh
sudo apt-get install netplan.io -y
```

[Using DHCP and static addressing via `netplan`](https://netplan.io/examples#using-dhcp-and-static-addressing)

```sh
sudo netplan apply
```


```sh
sudo vim /etc/hosts
```

```txt
127.0.0.1       localhost
127.0.1.1       pydemia-jn00 # Its own hostname


192.168.2.11   kube-jn00
192.168.2.12   kube-jn01
192.168.2.13   kube-jn02
192.168.2.14   kube-jn03
```

```diff
-sudo hostnamectl set-hostname master-node
```


```sh
sudo apt-get update && sudo apt-get install -y apt-transport-https curl

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
sudo apt-get update

#apt list -a kubeadm
sudo apt-get install -y kubelet=1.15.10-00 kubeadm=1.15.10-00 kubectl=1.15.10-00 --allow-downgrades --allow-change-held-packages
sudo apt-mark hold kubelet kubeadm kubectl

```


### Configuring the master node

```sh
sudo vim /etc/bash.bashrc
```

As `ROOT`:
```sh
export API_ADDR="192.168.2.11"  # Master Server external IP
export DNS_DOMAIN="k8s.local"
export POD_NET="10.100.0.0/16"   # k8s cluster POD Network CIDR
```

For chaining the bridged network traffic to `iptables`:

```sh
sysctl net.bridge.bridge-nf-call-iptables=1

vim /etc/sysctl.conf

net.bridge.bridge-nf-call-iptables=1
net.bridge.bridge-nf-call-ip6tables=1
net.netfilter.nf_conntrack_max = 786432

```



```sh
kubeadm init \
 --pod-network-cidr=${POD_NET} \
 --apiserver-advertise-address ${API_ADDR} \
 --service-dns-domain "${DNS_DOMAIN}" \
 --kubernetes-version "1.15.10"
 
```


```txt

[init] Using Kubernetes version: v1.15.10
[preflight] Running pre-flight checks
[preflight] Pulling images required for setting up a Kubernetes cluster
[preflight] This might take a minute or two, depending on the speed of your internet connection
[preflight] You can also perform this action in beforehand using 'kubeadm config images pull'
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Activating the kubelet service
[certs] Using certificateDir folder "/etc/kubernetes/pki"
[certs] Generating "ca" certificate and key
[certs] Generating "apiserver-kubelet-client" certificate and key
[certs] Generating "apiserver" certificate and key
[certs] apiserver serving cert is signed for DNS names [pydemia-jn00 kubernetes kubernetes.default kubernetes.default.svc kubernetes.default.svc.k8s.local] and IPs [10.96.0.1 192.168.2.11]
[certs] Generating "front-proxy-ca" certificate and key
[certs] Generating "front-proxy-client" certificate and key
[certs] Generating "etcd/ca" certificate and key
[certs] Generating "etcd/server" certificate and key
[certs] etcd/server serving cert is signed for DNS names [pydemia-jn00 localhost] and IPs [192.168.2.11 127.0.0.1 ::1] [certs] Generating "etcd/peer" certificate and key
[certs] etcd/peer serving cert is signed for DNS names [pydemia-jn00 localhost] and IPs [192.168.2.11 127.0.0.1 ::1]   [certs] Generating "etcd/healthcheck-client" certificate and key
[certs] Generating "apiserver-etcd-client" certificate and key
[certs] Generating "sa" key and public key
[kubeconfig] Using kubeconfig folder "/etc/kubernetes"
[kubeconfig] Writing "admin.conf" kubeconfig file
[kubeconfig] Writing "kubelet.conf" kubeconfig file
[kubeconfig] Writing "controller-manager.conf" kubeconfig file
[kubeconfig] Writing "scheduler.conf" kubeconfig file
[control-plane] Using manifest folder "/etc/kubernetes/manifests"
[control-plane] Creating static Pod manifest for "kube-apiserver"
[control-plane] Creating static Pod manifest for "kube-controller-manager"
[control-plane] Creating static Pod manifest for "kube-scheduler"
[etcd] Creating static Pod manifest for local etcd in "/etc/kubernetes/manifests"
[wait-control-plane] Waiting for the kubelet to boot up the control plane as static Pods from directory "/etc/kubernetes/manifests". This can take up to 4m0s
[kubelet-check] Initial timeout of 40s passed.
[apiclient] All control plane components are healthy after 61.562702 seconds
[upload-config] Storing the configuration used in ConfigMap "kubeadm-config" in the "kube-system" Namespace
[kubelet] Creating a ConfigMap "kubelet-config-1.15" in namespace kube-system with the configuration for the kubelets in the cluster
[upload-certs] Skipping phase. Please see --upload-certs
[mark-control-plane] Marking the node pydemia-jn00 as control-plane by adding the label "node-role.kubernetes.io/master=''"
[mark-control-plane] Marking the node pydemia-jn00 as control-plane by adding the taints [node-role.kubernetes.io/master:NoSchedule]
[bootstrap-token] Using token: eh062q.qi5w233jg8fqhck7
[bootstrap-token] Configuring bootstrap tokens, cluster-info ConfigMap, RBAC Roles
[bootstrap-token] configured RBAC rules to allow Node Bootstrap tokens to post CSRs in order for nodes to get long term certificate credentials
[bootstrap-token] configured RBAC rules to allow the csrapprover controller automatically approve CSRs from a Node Bootstrap Token
[bootstrap-token] configured RBAC rules to allow certificate rotation for all node client certificates in the cluster
[bootstrap-token] Creating the "cluster-info" ConfigMap in the "kube-public" namespace
[addons] Applied essential addon: CoreDNS
[addons] Applied essential addon: kube-proxy

Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.2.11:6443 --token eh062q.qi5w233jg8fqhck7 \
    --discovery-token-ca-cert-hash sha256:e41cf058852c7f3b46ae0d9be2d6ab1cc0005c5702da0601479851209b195f68

```


#### Set Master

```sh
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=$HOME/.kube/config
echo "export KUBECONFIG=$HOME/.kube/config" | tee -a ~/.bashrc

```

* Pod Networking via `Calico`(used by Google)
```sh
wget https://docs.projectcalico.org/v3.9/manifests/calico.yaml
vim calico.yaml

```

```yaml
- name: CALICO_IPV4POOL_CIDR
  value: "10.100.0.0/16"
```


```sh
kubectl apply -f ./calico.yaml

wget https://docs.projectcalico.org/v3.9/getting-started/kubernetes/installation/hosted/kubernetes-datastore/calicoctl.yaml
kubectl apply -f ./calicoctl.yaml

sudo vim /etc/bash.bashrc
alias calicoctl="kubectl exec -i -n kube-system calicoctl /calicoctl -- "


configmap/calico-config created
customresourcedefinition.apiextensions.k8s.io/felixconfigurations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamblocks.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/blockaffinities.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamhandles.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamconfigs.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/bgppeers.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/bgpconfigurations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ippools.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/hostendpoints.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/clusterinformations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/globalnetworkpolicies.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/globalnetworksets.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/networkpolicies.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/networksets.crd.projectcalico.org created
clusterrole.rbac.authorization.k8s.io/calico-kube-controllers created
clusterrolebinding.rbac.authorization.k8s.io/calico-kube-controllers created
clusterrole.rbac.authorization.k8s.io/calico-node created
clusterrolebinding.rbac.authorization.k8s.io/calico-node created
daemonset.extensions/calico-node created
serviceaccount/calico-node created
deployment.extensions/calico-kube-controllers created
serviceaccount/calico-kube-controllers created
```

```sh
kubectl get nodes

NAME           STATUS   ROLES    AGE     VERSION
pydemia-jn00   Ready    master   2m36s   v1.15.10
```

```sh
watch kubectl get pods --all-namespaces

```

#### Set Nodes

AS `ROOT`:
```sh
kubeadm join 192.168.2.11:6443 --token vdtl8i.ilk45ovj00xussa5 \
    --discovery-token-ca-cert-hash sha256:dec491861bdf757dee5fa0c892e87f58674cbb62cfcd0dac77b4db9847f6866e

```


#### Check

```sh
kubectl label node pydemia-jn01 node-role.kubernetes.io/worker=worker
kubectl label node pydemia-jn02 node-role.kubernetes.io/worker=worker
kubectl label node pydemia-jn03 node-role.kubernetes.io/worker=worker
```

```sh
kubectl get nodes

NAME           STATUS   ROLES    AGE   VERSION
pydemia-jn00   Ready    master   37m   v1.15.10
pydemia-jn01   Ready    worker   24m   v1.15.10
pydemia-jn02   Ready    worker   24m   v1.15.10
pydemia-jn03   Ready    worker   23m   v1.15.10

```

```sh
watch kubectl get pods --all-namespaces

```


If needed:
```sh
kubeadm reset -f
```


#### Test

```sh
vim gpu-test.yml
```

```yml
apiVersion: v1
kind: Pod
metadata:
  name: devicequery
spec:
  containers:
    - name: nvidia
      image: pydemia/nvidia-jetson-nano:latest
      command: [ "./deviceQuery" ]

```

```sh
kubectl apply -f gpu-test.yml
# pod/devicequery created

kubectl logs devicequery

```



```sh
systemctl restart kubelet
```


### Dashboard


#### Get Certificates

```sh
mkdir ~/certs
cd ~/certs

openssl genrsa -des3 -passout pass:x -out dashboard.pass.key 2048
openssl rsa -passin pass:x -in dashboard.pass.key -out dashboard.key
openssl req -new -key dashboard.key -out dashboard.csr
openssl x509 -req -sha256 -days 365 -in dashboard.csr -signkey dashboard.key -out dashboard.crt

```

#### Recommended Setup

```sh
kubectl create secret generic kubernetes-dashboard-certs --from-file=$HOME/certs -n kube-system

```


#### Set NodePort

```sh
kubectl edit service kubernetes-dashboard -n kube-system
```

```txt
# Please edit the object below. Lines beginning with a '#' will be ignored,
# and an empty file will abort the edit. If an error occurs while saving this file will be
# reopened with the relevant failures.
#
apiVersion: v1
kind: Service
metadata:
annotations:
   kubectl.kubernetes.io/last-applied-configuration: |
     {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"k8s-app":"kubernetes-dashboard"},"name":"kubernetes-dashboard","namespace":"kube-system"},"spec":{"ports":[{"port":443,"targetPort":8443}],"selector":{"k8s-app":"kubernetes-dashboard"}}}
creationTimestamp: 2018-12-24T04:27:04Z
labels:
   k8s-app: kubernetes-dashboard
name: kubernetes-dashboard
namespace: kube-system
resourceVersion: "1748"
selfLink: /api/v1/namespaces/kube-system/services/kubernetes-dashboard
uid: 2a4888ce-0734-11e9-9162-000c296423b3
spec:
clusterIP: 10.100.194.126
externalTrafficPolicy: Cluster
ports:
- nodePort: 31055
   port: 443
   protocol: TCP
   targetPort: 8443
selector:
   k8s-app: kubernetes-dashboard
sessionAffinity: None
type: NodePort
status:
loadBalancer: {}
```

#### Check

```sh
kubectl get service -n kube-system
```

#### Create an account

```sh
kubectl create serviceaccount cluster-admin-dashboard-sa
kubectl create clusterrolebinding cluster-admin-dashboard-sa --clusterrole=cluster-admin --serviceaccount=default:cluster-admin-dashboard-sa
```

#### Check token info

```sh
kubectl get secret $(kubectl get serviceaccount cluster-admin-dashboard-sa -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode

```

