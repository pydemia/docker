docker build . -t gcr.io/ds-ai-platform/microorganism:v0.1.0-http
docker run --rm --name mo -it -p 6006:6006/tcp -p 8501:8501/tcp -p 8888:8888/tcp gcr.io/ds-ai-platform/microorganism:v0.1.0-http