FROM python:3.9-slim
RUN apt-get -y update \
    && apt-get -y install vim \
        curl \
        python3-pip \
        libssl-dev \
        ffmpeg libsm6 libxext6 libxrender-dev \
        poppler-utils \
        antiword \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pip==22.3.1 \
    && pip3 install ipython \
    && pip3 install cmake \
    && apt-get clean
ADD ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENV SRC_DIR /dult-ai/
WORKDIR ${SRC_DIR}
ADD ./src ${SRC_DIR}/src/
COPY requirements.txt $SRC_DIR/
RUN  pip3 install -r requirements.txt
RUN python3.9 -m playwright install
RUN python3.9 -m playwright install-deps
ENV AWS_ACCESS_KEY_ID = "AKIAVQW7UWRUV7VG3ZXV"
ENV AWS_SECRET_ACCESS_KEY = "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"
ENV AWS_DEFAULT_REGION = "us-east-1"
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]