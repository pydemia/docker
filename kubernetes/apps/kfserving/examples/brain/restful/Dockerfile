FROM microorganism:v0.1

RUN mkdir -p /models
WORKDIR /tmp/skipc_microorganism_detection_model

RUN pip install \
    contextlib2 opencv-python Flask flask-restful jsonify

COPY __init__.py /tmp/skipc_microorganism_detection_model/modai/__init__.py
COPY model.py /tmp/skipc_microorganism_detection_model/
COPY runserver.py /tmp/skipc_microorganism_detection_model/
COPY init_entrypoint.sh /usr/local/bin/

RUN chmod u+x /usr/local/bin/init_entrypoint.sh
EXPOSE 8501
ENTRYPOINT ["init_entrypoint.sh"]