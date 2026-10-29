FROM debian@sha256:1e1a22175fbf1b32157ddaf0219e1db4e5401fab2b94ed285add64d18587cd2d

RUN apt-get update \
    && apt-get install -y --no-install-recommends socat ca-certificates \
    && rm -rf /var/lib/apt/lists/*

USER 991:982

ENTRYPOINT ["/usr/bin/socat"]
