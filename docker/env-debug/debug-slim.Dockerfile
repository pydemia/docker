FROM ubuntu:20.04
LABEL maintainer="Youngju Jaden Kim <pydemia@gmail.com>"

# ENV DEBIAN_FRONTEND noninteractive
# RUN apt update && \
#     apt install -y -qq dnsutils curl git vim


SHELL ["/bin/bash", "-c"]

RUN mkdir -p /workdir
WORKDIR /workdir

RUN apt-get update -q && \
    echo "69" | echo "6" | apt install -y -qq dnsutils && \
    apt-get install -y curl software-properties-common \
    git vim bash-completion unzip tree \
    apt-transport-https ca-certificates iputils-ping \
    gnupg jq python3.8 python3-pip 

# Add 3.8 to the available alternatives and set python3.8 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 && \
    update-alternatives --set python /usr/bin/python3.8 && \
    pip3 install --upgrade pip && pip install jq

RUN apt-get install -y bash-completion
RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/pydemia/pydemia-theme/master/install_themes.sh)"


# kubectl
ENV KUBECTL_VERSION="v1.20.0"
RUN curl -fsSL -O https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/kubectl

RUN echo 'source <(kubectl completion bash)' >> /etc/bash.bashrc

COPY trademark.sh trademark.sh
RUN cat trademark.sh >> /etc/bash.bashrc && rm trademark.sh

COPY commands.sh commands.sh
RUN cat commands.sh >> /etc/bash.bashrc && rm commands.sh

RUN rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# ENTRYPOINT ["/bin/bash"]
