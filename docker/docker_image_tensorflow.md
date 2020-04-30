# Docker Image setting

## Installation

```sh
docker run -d -p 8888:8888 -p 6006:6006 tensorflow/tensorflow
docker ps
docker exec -it <containerID> bash
#
```

```sh
apt-get update
apt-get install vim -y
```

### `jupyter_notebook_config.py`

```sh
vim /root/.jupyter/jupyter_notebook_config.py
vim ~/.bashrc
```

```vim
export PASSWORD=""
```

```sh
exit
```

```sh
docker ps
```

Commit:
```sh
docker commit <containerID> <new_image_name>
docker commit 8120 lecture_anomaly_detection
```


## Stop and Run
```sh
docker ps
docker stop <containerID>
docker stop -a
```


Run it:
```sh
docker run -it -p 8888:8888 -p 6006:6006 lecture_anomaly_detection
```


## Customizing

```sh
pip install conda
```
