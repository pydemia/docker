FROM ubuntu:20.04
LABEL maintainer="Youngju Jaden Kim <pydemia@gmail.com>"

# ENV DEBIAN_FRONTEND noninteractive
# RUN apt update && \
#     apt install -y -qq dnsutils curl git vim

RUN apt update && \
    echo "69" | echo "6" | apt install -y -qq dnsutils && \
    apt install -y curl git vim bash-completion

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/pydemia/pydemia-theme/master/install_themes.sh)"

RUN rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

ENTRYPOINT ["/bin/bash"]
