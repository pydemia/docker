```sh
TF_VERSION=1.12.0 #1.11.0, 1.10.0
docker pull tensorflow/serving:$TF_VERSION
```

```sh
docker run --rm --name=tf_base -d  -p 8500:8500/tcp -p 8501:8501/tcp tensorflow/serving:1.12.0 
docker cp tf_base:/usr/bin/tf_serving_entrypoint.sh ./tf_serving_entrypoint.sh


docker exec -it tf_base /bin/sh -c "[ -e /bin/bash ] && /bin/bash || /bin/sh"
docker cp tf_base:/usr/bin/tf_serving_entrypoint.sh ./tf_serving_entrypoint.sh
docker cp tf_base:/usr/bin/tensorflow_model_server ./tensorflow_model_server
```

```sh
tensorflow_model_server --port=8500 --rest_api_port=8501 --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} "$@"
```
