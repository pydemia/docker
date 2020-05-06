# Create a Kubernetes cluster on NVIDIA Jetson Nano

* Master: 1  
* Worker: 3  
* NFS   : 1

## Table of Contents
* [Prerequisite](#prerequisite)
  * [Boot-up](#boot-up)
  * [Network Config](#network-config)
  * [System Basic Settings](#system-basic-settings)
  * [Docker Setting](#docker-setting)
    * [NVIDIA Runtime for Docker](#nvidia-runtime-for-docker-set-the-nvidia-runtime-as-a-default-runtime-in-docker)
  * [Teset GPU on Docker](#test-gpu-on-docker)
  * [Kubernetes Setting](#kubernetes-setting)
    * [NTP](#ntp-time-server-sync)
    * [Docker on](#docker-service-on)
    * [Port Allocation & Firewall](#port-allocation)
* [Install Kubernetes](#install-kubernetes)
  * [Add Kubernetes Repository & Install Kubernetes on all resources](#add-kubernetes-repository--install-kubernetes-on-all-resources)
  * [Initialize a Kubernetes Cluster](#initialize-a-kubernetes-cluster)
  * [Install `cni`](#install-cni)
    * [Cluster Networking via `calico`](#cluster-networking-via-calicoused-by-google)
    * [`calicoctl` application as a pod](#calicoctl-application-as-a-pod)
    * [(Optional)Cluster Networking via `flannel`](#optional-cluster-networking-via-flannel)
  * [Check the cluster](#check-the-cluster)
    * [Calico Setting](#calico-setting)
    * [Test](#test)
      * [Docker Registry Authentication](#docker-registry-authentication)
* Manage Kubernetes
  * Dashboard

## Prerequisite

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



### System Basic Settings

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
Add current user to docker group to use docker command without sudo, following this guide:  
https://docs.docker.com/install/linux/linux-postinstall/.  
The required commands are following:
```bash
sudo groupadd docker # already exists in `r32.4.2`.
sudo usermod -aG docker $USER
newgrp docker  # to change the current group ID (GID) during a login session.
```

#### NVIDIA Runtime for Docker-Set the `NVidia runtime` as a default runtime in Docker.

Default:
`cat /etc/docker/daemon.json`
```json
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
    },
    "exec-opts": ["native.cgroupdriver=systemd"],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m"
    },
    "storage-driver": "overlay2"
}

EOF
```

* From
  * [github-NVIDIA default runtime](https://github.com/NVIDIA/nvidia-docker/wiki/Advanced-topics#default-runtime)
  * [kube-cgroup-drivers(ENG)](https://kubernetes.io/docs/setup/production-environment/#cgroup-drivers)
  * [kube-cgroup-drivers(KOR)](https://kubernetes.io/ko/docs/setup/production-environment/#cgroup-%EB%93%9C%EB%9D%BC%EC%9D%B4%EB%B2%84)

* [Docker Storage Drivers](https://docs.docker.com/storage/storagedriver/select-storage-driver/)  

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


##### Set Environment variables for `cuda`: (`/etc/bash.bashrc` and `/etc/profile`)

* Check `cuda version` installed
```sh
ls /usr/local |grep cuda
#----------#
lrwxrwxrwx  1 root root    9 Apr 19 11:57 cuda -> cuda-10.2
drwxr-xr-x 12 root root 4096 Apr 19 11:57 cuda-10.2
```

* Append `env_var`s
```bash
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

### Test GPU on Docker

From <https://ngc.nvidia.com/catalog/containers>  
* Base: `docker pull nvcr.io/nvidia/l4t-base:r32.4.2`
* ML: `docker pull nvcr.io/nvidia/l4t-ml:r32.4.2-py3`
* Tensorflow: `docker pull nvcr.io/nvidia/l4t-tensorflow:r32.4.2-tf1.15-py3`
* PyTorch: `docker pull nvcr.io/nvidia/l4t-pytorch:r32.4.2-pth1.5-py3`


#### Building CUDA in Containers on Jetson (Master)  
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

#### Push it
```sh
docker login
docker push pydemia/nvidia-jn-devicequery:r32.4.2
```

#### Run it
Test a Docker image.  
we are ready to test if Docker runs correctly and supports GPU.  
To make this easier, we created a dedicated Docker image with `deviceQuery` tool  
from the CUDA SDK which is used to query the GPU and present its capabilities.  
The command to run it is simple:
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

---
### Kubernetes Setting

* Time server sync with `ntp`
* Docker service enabled
* Static IP Address
* no Memory SWAP
* Port Allocation & Firewall Setting

#### NTP Time Server Sync

Prerequisite:
```sh
sudo apt install -y ntp
```

##### On MASTER:
Add the following to provide your current local time as a default.  
you should temporarily lose Internet connectivity:

```sh
echo '
server 127.127.1.0
fudge 127.127.1.0 stratum 10
' | sudo tee -a /etc/ntp.conf
```

Then Restart NTP:
```sh
sudo /etc/init.d/ntp restart
```

##### On WORKER:

On all the remaining nodes in your cluster,  
set them up to sync clocks with the node which was designated as the main time server in the cluster.

* Declare the pool's domain name with a `pool` command (and not `server`)*

`/etc/ntp.conf`
```diff
-server <main time server> iburst
+pool <main time server> iburst
```
[pool Directive vs. server Lines](https://kb.meinbergglobal.com/kb/time_sync/ntp/configuration/ntp_pool_usage#pool_directive_vs_server_lines)


`/etc/ntp.conf`:
```sh
# Specify one or more NTP servers.
server kube-jn00 iburst

# Use servers from the NTP Pool Project. Approved by Ubuntu Technical Board
# on 2011-02-08 (LP: #104525). See http://www.pool.ntp.org/join.html for
# more information.
#pool 0.ubuntu.pool.ntp.org iburst
#pool 1.ubuntu.pool.ntp.org iburst
#pool 2.ubuntu.pool.ntp.org iburst
#pool 3.ubuntu.pool.ntp.org iburst

# Use Ubuntu's ntp server as a fallback.
#pool ntp.ubuntu.com

...
```

Then Restart NTP:
```sh
sudo /etc/init.d/ntp restart
```

Check Connectivity to the main server:
```sh
ntpq -c lpeer
```

```sh
pydemia@kube-jn01:~$ ntpq -c lpeer
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*kube-jn00       46.243.26.34     2 u    2   64    1    1.266  -27.718   0.774
```

* (Info) When running the same command on the main server at the same time:
```sh
pydemia@kube-jn00:~$ ntpq -c lpeer
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
 0.ubuntu.pool.n .POOL.          16 p    -   64    0    0.000    0.000   0.000
 1.ubuntu.pool.n .POOL.          16 p    -   64    0    0.000    0.000   0.000
 2.ubuntu.pool.n .POOL.          16 p    -   64    0    0.000    0.000   0.000
 3.ubuntu.pool.n .POOL.          16 p    -   64    0    0.000    0.000   0.000
 ntp.ubuntu.com  .POOL.          16 p    -   64    0    0.000    0.000   0.000
 LOCAL(0)        .LOCL.          10 l 1045   64    0    0.000    0.000   0.000
-ntp8.flashdance 192.36.143.151   2 u   31   64  377  293.367   28.453  10.973
*46.243.26.34 (4 .GPS.            1 u   38   64  377  270.858   17.212   8.267
#195.50.171.101  145.253.2.212    2 u  101   64  362  281.393    1.280  18.028
+78.156.103.10   193.162.159.194  2 u   35   64  377  293.255   31.363  10.559
+nsa.lds.net.ua  128.0.142.251    3 u   37   64  377  313.546   36.711   7.618
-213.251.52.250  195.66.241.10    2 u   42   64  245  257.189    5.322  21.922
+tethys.hot-chil 131.188.3.222    2 u  105   64  376  273.004   34.414  13.046
#ntp2.0x00.lv    131.188.3.221    2 u   44   64  377  307.520   21.495  12.015
#time.cloudflare 10.51.8.166      3 u   43   64  377   44.800   10.580  12.267
+alphyn.canonica 132.163.96.1     2 u   65   64  377  211.766   21.924  10.917
+re.uni-paderbor .DCF.            1 u   36   64  377  295.706   32.057  10.841
-ns1.alza.is     85.199.214.98    2 u   34   64  377  311.954   30.566   8.215
+zero.gotroot.ca 214.176.184.39   2 u   29   64  377  155.720   13.616  10.911
```

#### Docker service on

* Enable docker service
```sh
sudo systemctl daemon-reload
sudo systemctl enable docker
sudo systemctl restart docker
```

* Set `native.cgroupdriver=systemd`
```sh
sudo tee /etc/docker/daemon.json << EOF
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    },
    "exec-opts": ["native.cgroupdriver=systemd"],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m"
    },
    "storage-driver": "overlay2"
}

EOF
```

#### Port allocation

From [kube-check required ports](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#check-required-ports)  
From [coreos-kube networking](https://github.com/coreos/coreos-kubernetes/blob/master/Documentation/kubernetes-networking.md)

The information below describes a minimum set of port allocations used by Kubernetes components.  
Some of these allocations will be optional depending on the deployment (e.g. if `flannel` or `calico` is being used).  
Additionally, there are likely additional ports a deployer will need to open on their infrastructure (e.g. `22/ssh`).

* Master Node Inbound

| Protocol | Port Range | Source                                    | Purpose                |
-----------|------------|-------------------------------------------|------------------------|
| TCP      | 443        | Worker Nodes, API Requests, and End-Users | Kubernetes API server. |
| UDP      | 8285       | Master & Worker Nodes                   | flannel overlay network - *udp backend*. This is the default network configuration (only required if using flannel) |
| UDP      | 8472       | Master & Worker Nodes                   | flannel overlay network - *vxlan backend* (only required if using flannel) |

* Worker Node Inbound

| Protocol | Port Range  | Source                         | Purpose                                                                |
-----------|-------------|--------------------------------|------------------------------------------------------------------------|
| TCP      | 10250       | Master Nodes                   | Worker node Kubelet API for exec and logs.                                  |
| TCP      | 10255       | Heapster                       | Worker node read-only Kubelet API.                                  |
| TCP      | 30000-32767 | External Application Consumers | Default port range for [external service][external-service] ports. Typically, these ports would need to be exposed to external load-balancers, or other external consumers of the application itself. |
| TCP      | ALL         | Master & Worker Nodes          | Intra-cluster communication (unnecessary if `vxlan` is used for networking)           |
| UDP      | 8285        | Master & Worker Nodes                   | flannel overlay network - *udp backend*. This is the default network configuration (only required if using flannel) |
| UDP      | 8472        | Master & Worker Nodes                   | flannel overlay network - *vxlan backend* (only required if using flannel) |
| TCP      | 179         | Worker Nodes                   | Calico BGP network (only required if the BGP backend is used) |

* `etcd` Node Inbound

| Protocol | Port Range | Source        | Purpose                                                  |
-----------|------------|---------------|----------------------------------------------------------|
| TCP      | 2379-2380  | Master Nodes  | etcd server client API                                   |
| TCP      | 2379-2380  | Worker Nodes  | etcd server client API (only required if using flannel or Calico). |


##### Install `ufw`

```sh
sudo apt install -y ufw
sudo ufw allow ssh
sudo ufw allow 22
sudo ufw enable
sudo systemctl enable ufw
sudo systemctl start ufw
```

In case of Error `ufw`, failed with
  `ip6tables-restore: line 142 failed; Problem running '/etc/ufw/before6.rules'`.  
It seems to be raised with `ipv6`, then:
```bash
sudo sed -i -e 's?IPV6=yes?IPV6=no?g' /etc/default/ufw
sudo shutdown -r now
```
Check it works:
```bash
sudo systemctl status ufw
```


##### Master Node

```bash
sudo ufw allow 6443,443,2379:2380,10250:10255/tcp
sudo ufw allow 8285,8472/udp

# Just in case, CNI_CIDR
sudo ufw allow from 192.168.99.0/24
```

##### Worker Node

```bash
sudo ufw allow 10250:10255,30000:32767,179,2379:2380/tcp
sudo ufw allow 8285,8472/udp

# Just in case, CNI_CIDR
sudo ufw allow from 192.168.99.0/24
```

##### Using `iptables`

```bash
sudo apt install -y iptables iptables-persistent netfilter-persistent

sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Master
sudo iptables -A INPUT -p tcp --match multiport  --dport 6443,443,2379:2380,10250:10255 -j ACCEPT
sudo iptables -A INPUT -p udp --match multiport  --dport 8285,8472 -j ACCEPT

# Worker
sudo iptables -A INPUT -p tcp --match multiport  --dport 10250:10255,30000:32767,179,2379:2380 -j ACCEPT
sudo iptables -A INPUT -p udp --match multiport  --dport 8285,8472 -j ACCEPT

```


---
## Install Kubernetes

### Add Kubernetes Repository & Install Kubernetes on all resources

#### Add repository: Kubernetes
```bash
sudo apt-get update && sudo apt-get install -y apt-transport-https curl && \
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - && \
cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
```

#### Install `kubeadm`

```bash
sudo apt list -a <package name>
```

```bash
sudo apt-get update && \
sudo apt-get install -y \
  kubelet=1.15.10-00 \
  kubeadm=1.15.10-00 \
  kubectl=1.15.10-00 \
  kubernetes-cni=0.7.5-00 \
  --allow-downgrades \
  --allow-change-held-packages
```

Fix kubernetes versions:
```sh
sudo apt-mark hold kubelet kubeadm kubectl kubernetes-cni
```

remove it:
```sh
sudo apt-get purge kubeadm kubectl kubelet kubernetes-cni kube*
sudo apt autoremove
```

#### (Optional) for `CRI` Runtime


* For `containerd`

As `ROOT`:
```sh
cat > /etc/modules-load.d/containerd.conf <<EOF
overlay
br_netfilter
EOF

modprobe overlay
modprobe br_netfilter

# Setup required sysctl params, these persist across reboots.
cat > /etc/sysctl.d/99-kubernetes-cri.conf <<EOF
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.ipv4.conf.all.forwarding        = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sysctl --system

sudo sysctl net.ipv4.conf.all.forwarding=1
sudo iptables -P FORWARD ACCEPT
```


#### (Optional) Static IP Addressing
* Static IP addressing  
```sh
sudo apt-get install netplan.io -y
sudo netplan apply
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
127.0.1.1       kube-jn00 # Its own hostname


192.168.2.11   kube-jn00
192.168.2.12   kube-jn01
192.168.2.13   kube-jn02
192.168.2.14   kube-jn03
```

```diff
-sudo hostnamectl set-hostname master-node
echo $HOSTNAME
```

### Initialize a Kubernetes Cluster

If a cluster exists, Remove it by the following:
```sh
rm -rf /etc/kubernetes
rm -rf /var/lib/etcd
kubeadm reset
```

#### On MASTER:
* for `flannel` as a cluster network interface  
(use Overaly Network Mechanism-linux bridge or ovs(L2)):
```sh
echo '
export API_ADDR="192.168.2.11"      # Master Server external IP
export DNS_DOMAIN="k8cluster.local" # default: "cluster.local"
export POD_NET="10.244.0.0/16"    # k8s cluster POD Network CIDR
# `POD_NET` for flannel: 10.244.0.0/16, calico: 192.168.0.0/16
' | sudo tee -a /etc/bash.bashrc
```

* for `calico` as a cluster network interface  
(use BGP routing protocol(L3)):
```sh
echo '
export API_ADDR="192.168.2.11"      # Master Server external IP
export DNS_DOMAIN="k8cluster.local" # default: "cluster.local"
export POD_NET="192.168.99.0/24"    # k8s cluster POD Network CIDR
# `POD_NET` for flannel: 10.244.0.0/16, calico: 192.168.0.0/16
' | sudo tee -a /etc/bash.bashrc
```

**_RUN THIS AS `ROOT`_**:
```sh
kubeadm init \
  --apiserver-advertise-address "${API_ADDR}" \
  --service-dns-domain "${DNS_DOMAIN}" \
  --pod-network-cidr=${POD_NET} \
  --kubernetes-version "1.15.10"
```

Note: this will autodetect the network interface to advertise the master on  
as the interface with the default gateway.  
If you want to use a different interface, specify `--apiserver-advertise-address <ip-address>` argument  
to `kubeadm init`.  

From <https://unofficial-kubernetes.readthedocs.io/en/latest/getting-started-guides/kubeadm/#24-initializing-your-master>

```ascii
[init] Using Kubernetes version: v1.15.10
[preflight] Running pre-flight checks
[preflight] Pulling images required for setting up a Kubernetes cluster
[preflight] This might take a minute or two, depending on the speed of your internet connection
[preflight] You can also perform this action in beforehand using 'kubeadm config images pull'
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Activating the kubelet service
[certs] Using certificateDir folder "/etc/kubernetes/pki"
[certs] Generating "front-proxy-ca" certificate and key
[certs] Generating "front-proxy-client" certificate and key
[certs] Generating "etcd/ca" certificate and key
[certs] Generating "etcd/peer" certificate and key
[certs] etcd/peer serving cert is signed for DNS names [kube-jn00 localhost] and IPs [192.168.2.11 127.0.0.1 ::1]
[certs] Generating "etcd/healthcheck-client" certificate and key
[certs] Generating "apiserver-etcd-client" certificate and key
[certs] Generating "etcd/server" certificate and key
[certs] etcd/server serving cert is signed for DNS names [kube-jn00 localhost] and IPs [192.168.2.11 127.0.0.1 ::1]
[certs] Generating "ca" certificate and key
[certs] Generating "apiserver" certificate and key
[certs] apiserver serving cert is signed for DNS names [kube-jn00 kubernetes kubernetes.default kubernetes.default.svc kubernetes.default.svc.k8cluster.local] and IPs [10.96.0.1 192.168.2.11]
[certs] Generating "apiserver-kubelet-client" certificate and key
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
[apiclient] All control plane components are healthy after 42.517189 seconds
[upload-config] Storing the configuration used in ConfigMap "kubeadm-config" in the "kube-system" Namespace
[kubelet] Creating a ConfigMap "kubelet-config-1.15" in namespace kube-system with the configuration for the kubelets in the cluster
[upload-certs] Skipping phase. Please see --upload-certs
[mark-control-plane] Marking the node kube-jn00 as control-plane by adding the label "node-role.kubernetes.io/master=''"
[mark-control-plane] Marking the node kube-jn00 as control-plane by adding the taints [node-role.kubernetes.io/master:NoSchedule]
[bootstrap-token] Using token: pv28di.rcmr8u0gza8hw4ee
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

kubeadm join 192.168.2.11:6443 --token pv28di.rcmr8u0gza8hw4ee \
    --discovery-token-ca-cert-hash sha256:5e74fed69a819dba76978f1959651cc2e61599624061e5933b12e6f04a544e91
```

#### On MASTER:
To start using your cluster, you need to run the following as a regular user:
```sh
mkdir -p $HOME/.kube
sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=$HOME/.kube/config
echo "export KUBECONFIG=$HOME/.kube/config" | tee -a ~/.bashrc
```

#### On WORKER, AS **_`ROOT`_**:
```sh
kubeadm join 192.168.2.11:6443 --token pv28di.rcmr8u0gza8hw4ee \
    --discovery-token-ca-cert-hash sha256:5e74fed69a819dba76978f1959651cc2e61599624061e5933b12e6f04a544e91
```

### Install `cni`

#### Cluster Networking via `calico`(used by Google)
**_CIDR Problem_ exists!_** *You should use `--pot-network-cidr=192.168.x.x/x` for `calico`!*

`192.168.0.0/16` -> `192.168.99.0/24`

> ```diff
> \- name: CALICO_IPV4POOL_CIDR
> ---  value: "192.168.0.0/16"
> +++  value: "192.168.99.0/24"
> ```

```bash
wget https://docs.projectcalico.org/v3.9/manifests/calico.yaml -O calico.yaml
sed -i -e 's?192.168.0.0/16?192.168.99.0/24?g' calico.yaml
kubectl apply -f calico.yaml
```

Messages:
```ascii
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
daemonset.apps/calico-node created
serviceaccount/calico-node created
deployment.apps/calico-kube-controllers created
serviceaccount/calico-kube-controllers created
```

#### `calicoctl` application as a pod:

In this article, `calicoctl version: v3.13.3` for now.
`docker pull calico/ctl:v3.13.3`

  - `etcd`
    ```sh
    kubectl apply -f https://docs.projectcalico.org/manifests/calicoctl-etcd.yaml
    ```

  - Kubernetes API datastore
    ```sh
     kubectl apply -f https://docs.projectcalico.org/manifests/calicoctl.yaml
    ```

You can then run commands using kubectl as shown below.
```sh
#kubectl exec -ti -n kube-system calicoctl -- /calicoctl get profiles -o wide
```

Create an `alias` as a command:
```sh
alias calicoctl="kubectl exec -i -n kube-system calicoctl /calicoctl -- "
```

```sh
echo '
alias calicoctl="kubectl exec -i -n kube-system calicoctl /calicoctl -- "
' | sudo tee -a /etc/bash.bashrc && \
source /etc/bash.bashrc && source ~/.bashrc
```


From [install-calicoctl-as-a-kube-pod](https://docs.projectcalico.org/getting-started/calicoctl/install#installing-calicoctl-as-a-kubernetes-pod)

#### (Optional) Cluster Networking via `flannel`
```sh
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/v0.11.0/Documentation/kube-flannel.yml
```


### Check the cluster

```bash
$ kubectl cluster-info
Kubernetes master is running at https://192.168.2.11:6443
KubeDNS is running at https://192.168.2.11:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

```sh
kubectl get nodes

NAME        STATUS   ROLES    AGE     VERSION
kube-jn00   Ready    master   4m49s   v1.15.10
kube-jn01   Ready    <none>   103s    v1.15.10
kube-jn02   Ready    <none>   85s     v1.15.10
kube-jn03   Ready    <none>   83s     v1.15.10
```

* Label it:
```sh
kubectl label node kube-jn01 node-role.kubernetes.io/worker=worker
kubectl label node kube-jn02 node-role.kubernetes.io/worker=worker
kubectl label node kube-jn03 node-role.kubernetes.io/worker=worker
```

> - Add a label: 
>   ```bash
>   kubectl label node <node name> node-role.kubernetes.io/<role name>=<key - (any name)>
>   ```
> - Remove a label:
>   ```bash
>   kubectl label node <node name> node-role.kubernetes.io/<role name>-
>   ```

* Check it Again:
```sh
kubectl get nodes

NAME        STATUS   ROLES    AGE     VERSION
kube-jn00   Ready    master   10m     v1.15.10
kube-jn01   Ready    worker   7m49s   v1.15.10
kube-jn02   Ready    worker   7m31s   v1.15.10
kube-jn03   Ready    worker   7m29s   v1.15.10
```

```sh
watch kubectl get pods --all-namespaces
alias kube-watch="watch -n 5 kubectl get pods --all-namespaces"
watch kubectl get pods --all-namespaces -o wide
```


```sh
kubectl get pods --namespace=kube-system -l k8s-app=kube-dns
```

If needed:
```sh
kubeadm reset -f
```


#### Calico Setting

```sh
kubectl get pods --all-namespaces

NAMESPACE     NAME                                       READY   STATUS                       RESTARTS   AGE
kube-system   calico-kube-controllers-56cd854695-99krw   1/1     Running                      0          6m34s
kube-system   calico-node-44sv8                          0/1     Running                      0          3m25s
kube-system   calico-node-69s5g                          0/1     Running                      0          6m34s
kube-system   calico-node-bkrxb                          0/1     Running                      0          3m35s
kube-system   calico-node-mq7kg                          0/1     Running                      0          3m34s
kube-system   calicoctl                                  0/1     CreateContainerConfigError   0          4m7s
kube-system   coredns-5d4dd4b4db-qlf9n                   1/1     Running                      0          12m
kube-system   coredns-5d4dd4b4db-qm4rs                   1/1     Running                      0          12m
kube-system   etcd-kube-jn00                             1/1     Running                      0          11m
kube-system   kube-apiserver-kube-jn00                   1/1     Running                      0          11m
kube-system   kube-controller-manager-kube-jn00          1/1     Running                      0          11m
kube-system   kube-proxy-5kvqh                           1/1     Running                      0          3m35s
kube-system   kube-proxy-bxvkk                           1/1     Running                      0          3m25s
kube-system   kube-proxy-jsmrl                           1/1     Running                      0          12m
kube-system   kube-proxy-zrjg6                           1/1     Running                      0          3m34s
kube-system   kube-scheduler-kube-jn00                   1/1     Running                      0          11m
```

```sh
kubectl logs -n kube-system calico-kube-controllers-56cd854695-twxwt

2020-05-02 21:48:40.805 [INFO][1] main.go 87: Loaded configuration from environment config=&config.Config{LogLevel:"info", ReconcilerPeriod:"5m", CompactionPeriod:"10m", EnabledControllers:"node", WorkloadEndpointWorkers:1, ProfileWorkers:1, PolicyWorkers:1, NodeWorkers:1, Kubeconfig:"", HealthEnabled:true, SyncNodeLabels:true, DatastoreType:"kubernetes"}
2020-05-02 21:48:40.809 [INFO][1] k8s.go 228: Using Calico IPAM
W0502 21:48:40.810016       1 client_config.go:541] Neither --kubeconfig nor --master was specified.  Using the inClusterConfig.  This might not work.
2020-05-02 21:48:40.812 [INFO][1] main.go 108: Ensuring Calico datastore is initialized
2020-05-02 21:48:50.813 [ERROR][1] client.go 255: Error getting cluster information config ClusterInformation="default" error=Get https://10.96.0.1:443/apis/crd.projectcalico.org/v1/clusterinformations/default: context deadline exceeded
2020-05-02 21:48:50.813 [FATAL][1] main.go 113: Failed to initialize Calico datastore error=Get https://10.96.0.1:443/apis/crd.projectcalico.org/v1/clusterinformations/default: context deadline exceeded
```

#### Test

If needed: `docker login` first.  
Then: `$HOME/.docker/config.json`


```sh
echo '
apiVersion: v1
kind: Pod
metadata:
  name: devicequery
spec:
  containers:
    - name: nvidia
      imagePullPolicy: IfNotPresent
      image: pydemia/nvidia-jn-devicequery:r32.4.2
      command: [ "./deviceQuery" ]
' | tee ~/gpu-test.yml

kubectl apply -f gpu-test.yml
```

```sh
kubectl apply -f gpu-test.yml
# pod/devicequery created

kubectl logs devicequery

```

```ascii
NAMESPACE     NAME                                       READY   STATUS                       RESTARTS   AGE
default       devicequery                                0/1     ContainerCreating            0          43s
kube-system   calico-kube-controllers-56cd854695-99krw   1/1     Running                      0          10m
kube-system   calico-node-44sv8                          0/1     Running                      0          7m30s
kube-system   calico-node-69s5g                          0/1     Running                      0          10m
kube-system   calico-node-bkrxb                          1/1     Running                      0          7m40s
kube-system   calico-node-mq7kg                          0/1     Running                      0          7m39s
kube-system   calicoctl                                  0/1     CreateContainerConfigError   0          8m12s
kube-system   coredns-5d4dd4b4db-qlf9n                   1/1     Running                      0          16m
kube-system   coredns-5d4dd4b4db-qm4rs                   1/1     Running                      0          16m
kube-system   etcd-kube-jn00                             1/1     Running                      0          15m
kube-system   kube-apiserver-kube-jn00                   1/1     Running                      0          15m
kube-system   kube-controller-manager-kube-jn00          1/1     Running                      0          15m
kube-system   kube-proxy-5kvqh                           1/1     Running                      0          7m40s
kube-system   kube-proxy-bxvkk                           1/1     Running                      0          7m30s
kube-system   kube-proxy-jsmrl                           1/1     Running                      0          16m
kube-system   kube-proxy-zrjg6                           1/1     Running                      0          7m39s
kube-system   kube-scheduler-kube-jn00                   1/1     Running                      0          15m
```


##### Docker Registry Authentication
```sh
kubectl create secret docker-registry docker-registry-login \
  --docker-server=<SERVER>:<PORT> \
  --docker-username=<USERNAME> \
  --docker-password=<PASSWORD> \
  --docker-email=pydemia@gmail.com \
  --namespace=default

secret/docker-registry-login created

kubectl get secrets
```


### Error

```sh
kubectl get endpoints kubernetes

NAME         ENDPOINTS           AGE
kubernetes   192.168.2.11:6443   43m
```

```sh
curl https://10.96.0.1:443/version

curl: (60) SSL certificate problem: unable to get local issuer certificate
More details here: https://curl.haxx.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
```


MARK HERE

### Dashboard

#### Kubernetes Dashboard

[github-kubernetes dashboard](https://github.com/kubernetes/dashboard)

* Deploy it:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```

or

```bash
wget https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml \
  -O kubernetes-dashboard-v2.0.0.yaml
kubectl apply -f kubernetes-dashboard-v2.0.0.yaml
```

kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.6.0/src/deploy/kubernetes-dashboard.yaml


```bash
wget https://raw.githubusercontent.com/kubernetes/dashboard/v1.6.0/src/deploy/kubernetes-dashboard.yaml \
  -O kubernetes-dashboard-v1.6.0.yaml
kubectl apply -f kubernetes-dashboard-v1.6.0.yaml
```


```ascii
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
secret/kubernetes-dashboard-certs created
secret/kubernetes-dashboard-csrf created
secret/kubernetes-dashboard-key-holder created
configmap/kubernetes-dashboard-settings created
role.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrole.rbac.authorization.k8s.io/kubernetes-dashboard created
rolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
service/dashboard-metrics-scraper created
deployment.apps/dashboard-metrics-scraper created


NAMESPACE              NAME                                         READY   STATUS    RESTARTS   AGE
...
kubernetes-dashboard   dashboard-metrics-scraper-76679bc5b9-vd9rg   1/1     Running   0          21m
kubernetes-dashboard   kubernetes-dashboard-7f9fd5966c-g59xx        0/1     Error     8          21m
```

* Access it:

```bash
kubectl proxy

Starting to serve on 127.0.0.1:8001
```
 Now access dashboard at:
 <http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/>

* Stop it:

```bash
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```

#### Get Certificates

[kubernetes dashboard-certificate management](https://github.com/kubernetes/dashboard/blob/master/docs/user/certificate-management.md#generate-private-key-and-certificate-signing-request)

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

