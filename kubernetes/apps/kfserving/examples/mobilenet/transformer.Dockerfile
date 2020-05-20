FROM python:3.7-slim

RUN mkdir -p /workspace
WORKDIR /workspace

COPY transformer/mobilenet_transformer.py mobilenet_transformer.py
COPY transformer/requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install kfserving
RUN pip install -r requirements.txt

RUN rm requirements.txt

ENTRYPOINT ["python", "-m", "mobilenet_transformer"]