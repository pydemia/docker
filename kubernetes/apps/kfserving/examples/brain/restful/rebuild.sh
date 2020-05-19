docker build --build-arg CUDA_VISIBLE_DEVICES=-1 . -t gcr.io/ds-ai-platform/microorganism:v0.1.0-http
docker build --build-arg CUDA_VISIBLE_DEVICES=0 . -t gcr.io/ds-ai-platform/microorganism:v0.1.0-http-gpu

docker push gcr.io/ds-ai-platform/microorganism:v0.1.0-http
docker push gcr.io/ds-ai-platform/microorganism:v0.1.0-http-gpu

docker tag gcr.io/ds-ai-platform/microorganism:v0.1.0-http pydemia/microorganism:v0.1.0-http
docker tag gcr.io/ds-ai-platform/microorganism:v0.1.0-http-gpu pydemia/microorganism:v0.1.0-http-gpu

docker push pydemia/microorganism:v0.1.0-http
docker push pydemia/microorganism:v0.1.0-http-gpu

docker run --rm --name mo -it \
  -p 8501:8501/tcp \
  -e MODEL_NAME="microorganism" \
  -e MODEL_BASE_PATH="/models" \
  gcr.io/ds-ai-platform/microorganism:v0.1.0-http
  