FROM pydemia/debug-slim
LABEL maintainer="Youngju Jaden Kim <pydemia@gmail.com>"

# ENV DEBIAN_FRONTEND noninteractive
# RUN apt update && \
#     apt install -y -qq dnsutils curl git vim

RUN apt-get update -q

# azul openjdk and maven
RUN apt-get install -y software-properties-common && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0xB1998361219BD9C9 && \
    apt-add-repository 'deb http://repos.azulsystems.com/ubuntu stable main' && \
    apt-get update -q && apt-get install -y zulu-14 maven=3.6.3-1

ENV JAVA_HOME="/usr/lib/jvm/zulu-14-amd64"


# google-cloud-sdk
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && \
    apt-get update -y && \
    apt-get install google-cloud-sdk -y

# aws cli 2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

# azure cli
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# k9s
RUN k9s_version="v0.24.2" && \
    k_os_type="linux" && \
    curl -L https://github.com/derailed/k9s/releases/download/"${k9s_version}"/k9s_"$(echo "${k_os_type}" |sed 's/./\u&/')"_x86_64.tar.gz -o k9s.tar.gz && \
    mkdir -p ./k9s && \
    tar -zxf k9s.tar.gz -C ./k9s && \
    mv ./k9s/k9s /usr/local/bin/ && \
    rm -rf ./k9s ./k9s.tar.gz && \
    echo "\nInstalled in: $(which k9s)"

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# ENTRYPOINT ["/bin/bash"]
