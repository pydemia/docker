# Docker Basics

## Installation

Ubuntu 16.04 


```sh
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates -y

sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
sudo vim /etc/apt/sources.list.d/docker.list
```

```vim
deb https://apt.dockerproject.org/repo ubuntu-xenial main
```

```sh
sudo apt-get update
sudo apt-get purge lxc-docker docker.io
sudo apt-get install docker-engine

```

## Start

```sh
sudo service docker start
sudo docker run hello-world
```

## Admin

Create `docker` group

```sh
sudo groupadd docker
sudo usermod -aG docker $USER
exit
docker run hello-world
```


`ufw` Setting

```sh
sudo ufw status
sudo ufw allow 2375/tcp
```

`DNS` Setting

```sh
sudo vim /etc/default/docker
```

Uncomment this:
```vim
DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"
```

Then
```sh
sudo service docker restart
```


AUTOSTART on boot
```sh
sudo systemctl enable docker
```
