FROM python:2.7-slim
MAINTAINER "Eau de Web" <cornel.nitu@eaudeweb.ro>

ENV WORK_DIR=/var/local/fgas-cache-server

RUN runDeps="curl vim build-essential netcat libmysqlclient-dev" \
 && apt-get update \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*

COPY . $WORK_DIR/
WORKDIR $WORK_DIR

RUN pip install -r requirements-dep.txt \
 && mv settings.py.example settings.py \
 && mv docker-entrypoint.sh /bin/

ENTRYPOINT ["docker-entrypoint.sh"]
