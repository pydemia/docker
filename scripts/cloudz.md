# Docker on CLOUD-Z


```sh
ssh-keygen -R <ip>
ssh root@<ip>

useradd skcc -m -s /bin/bash
visudo -f /etc/sudoers

apt-get update
apt-get install vim
apt-get install apt-transport-https ca-certificates -y
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
vim /etc/apt/sources.list.d/docker.list
deb https://apt.dockerproject.org/repo ubuntu-xenial main
apt-get update
apt-get install docker-engine
systemctl enable docker
service docker start
docker run hello-world

groupadd docker
usermod -aG docker $USER
ufw status
ufw allow 2375/tcp


```

## 
