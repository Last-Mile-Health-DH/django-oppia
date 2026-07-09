FROM python:3.12-slim-bullseye AS build

LABEL maintainer="Last Mile Health"

ARG NAME=OPPIA
ARG HOME_DIR=/usr/src/${NAME}

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    dos2unix \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*


RUN useradd -ms /bin/bash -d ${HOME_DIR} container_user \
    && mkdir -p ${HOME_DIR} /tmp/prometheus \
    && chown -R container_user: ${HOME_DIR} /tmp/prometheus

COPY requirements.txt /requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r /requirements.txt

COPY . ${HOME_DIR}
RUN touch ${HOME_DIR}/oppiamobile/settings_secret.py
RUN find ${HOME_DIR} -type f -print0 | xargs -0 dos2unix
RUN chmod +x ${HOME_DIR}/entrypoint.sh


FROM python:3.12-slim-bullseye

ARG NAME=OPPIA
ARG PORT=8000
ARG HOME_DIR=/usr/src/${NAME}

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash -d ${HOME_DIR} container_user \
    && mkdir -p /tmp/prometheus /usr/src/static /usr/src/media /usr/src/upload \
    && chown -R container_user: /tmp/prometheus /usr/src/static /usr/src/media /usr/src/upload

COPY --from=build /usr/local /usr/local
COPY --from=build --chown=container_user: ${HOME_DIR} ${HOME_DIR}

USER container_user
WORKDIR ${HOME_DIR}
EXPOSE ${PORT}

ENTRYPOINT ["sh", "./entrypoint.sh"]