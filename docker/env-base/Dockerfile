FROM ubuntu:18.04
LABEL maintainer="Youngju Jaden Kim <pydemia@gmail.com>"


RUN apt-get update && \
    apt-get install -y \
    # build-essential \
    # software-properties-common \
    # iputils-ping \
    curl \
    vim \
    # sudo \
    # htop \
    wget \
    # git \
    # # pkg-config \
    # python3 \
    # python3-pip \
    # python3-dev \
    # python3-setuptools \
    # python3-wheel \
    # ssh \
    # pbzip2 \
    bzip2 \
    # pv \
    unzip \
    #tree \
    ca-certificates
    #default-mysql-client


# GCLOUD
# RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
#   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && \
#   apt-get update -y && \
#   apt-get install google-cloud-sdk -y
# RUN curl -sL https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-291.0.0-linux-x86_64.tar.gz | tar -zxf - && \
#     ./google-cloud-sdk/install.sh && \
#     rm -rf ./google-cloud-sdk

# # AWS CLI 2
# RUN curl -sL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
#   unzip awscliv2.zip && \
#   ./aws/install && \
#   rm -rf awscliv2.zip ./aws

# # AZURE CLI
# RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Clean up `apt cache`
RUN apt-get clean && \
    apt-get autoclean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists

CMD ["/bin/bash"]