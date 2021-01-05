FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

# Creating working directory
RUN mkdir -p /app
WORKDIR /app

# Copying requirements
COPY requirements.txt .
COPY requirements/ /app/requirements/

RUN set -ex \
    && apk add bash \
    && apk add --no-cache --virtual .build-deps \
       gcc \
       python3-dev \
       libffi-dev \
       make \
       musl-dev \
    && apk add --no-cache mariadb-dev \
    && apk add --no-cache \
       gettext \
    && apk add --no-cache \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/community \
       gdal \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY docker-entrypoint.sh /app

COPY ./src/ ./src

RUN mkdir -p /app/src/static/

EXPOSE 8000

ENTRYPOINT ["sh", "docker-entrypoint.sh"]
