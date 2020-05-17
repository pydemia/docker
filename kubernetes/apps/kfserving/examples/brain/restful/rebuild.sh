docker build . -t gcr.io/ds-ai-platform/microorganism:v0.1.0-http

docker run --rm --name mo -it \
  -p 8501:8501/tcp \
  -e MODEL_NAME="microorganism" \
  -e MODEL_BASE_PATH="/models" \
  gcr.io/ds-ai-platform/microorganism:v0.1.0-http
  