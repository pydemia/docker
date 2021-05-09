FROM alpine:3.13.2
LABEL maintainer="Youngju Jaden Kim <pydemia@gmail.com>"

# ENV DEBIAN_FRONTEND noninteractive
# RUN apt update && \
#     apt install -y -qq dnsutils curl git vim

RUN apk update && \
    apk add --no-cache curl vim bash unzip tree git openssh \
    jq yq ca-certificates bash-completion gnupg mysql-client && \
    rm -rf /var/cache/apk/*
# shadow
# RUN apk cache --purge

RUN sed -i -e "s/bin\/ash/bin\/bash/" /etc/passwd
# RUN echo "auth       sufficient   pam_shells.so" > /etc/pam.d/chsh && \
#     chsh -s /bin/bash
ENV LC_ALL=en_US.UTF-8
SHELL ["/bin/bash", "-c"]

RUN mkdir -p /workdir
WORKDIR /workdir

# kubectl
ENV KUBECTL_VERSION="v1.20.0"
RUN curl -fsSL -O https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/kubectl
RUN echo 'source <(kubectl completion bash)' >> /etc/bash.bashrc

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/pydemia/pydemia-theme/master/install_themes.sh)"

COPY trademark.sh trademark.sh
RUN cat trademark.sh >> /etc/bash.bashrc && rm trademark.sh

COPY commands.sh commands.sh
RUN cat commands.sh >> /etc/bash.bashrc && rm commands.sh

# ENTRYPOINT ["/bin/bash"]
