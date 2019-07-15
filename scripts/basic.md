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

```sh
echo "export DOCKER_HOST=tcp://localhost:2375" >> ~/.zshrc
```

```sh
vim /lib/systemd/system/docker.service
```

```diff
-ExecStart=/usr/bin/dockerd -H fd://
+ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 fd://
```

## Create an `Container`

`Ubuntu 16.04` Image Download

```sh
docker run ubuntu:16.04
```

Then, Run this container:
```sh
docker run --rm -it ubuntu:16.04 /bin/bash
```

> run `/bin/bash` on init to enter the container.
> `-it` for keyboard. 쉘을 실행하고 키보드 입력을 위해 -it 옵션을 줍니다. 추가적으로 프로세스가 종료되면 컨테이너가 자동으로 삭제되도록 --rm 옵션도 추가하였습니다.
> `--rm` for eliminating the container on exit.
>


```sh
cat /etc/issue

ls

```

to exit:
```sh
exit
```


## Copy files

```sh
docker cp <containerID>:/foo.txt foo.txt
docker cp <containerID>:/foo.txt foo.txt
```


## Run

```sh
docker run -i -d -p 8888:8888 jupyter/tensorflow-notebook /bin/bash

docker exec -u root -it bash
```

## Login

```sh
docker login -u pydemia
docker tag lecture_analytics_dl pydemia/jupyter-notebook
docker push pydemia/jupyter-notebook

```


### Push & Pull Images in GCP

```sh
gcloud auth configure-docker
docker pull us.gcr.io/pydemia-cloud/tf-1-12-intel-mkl-v8cpu-30mem-300ssd

docker tag tf-1-12-intel-mkl-v8cpu-30mem-300ssd gcr.io/pydemia-cloud/jupyterhub

```


