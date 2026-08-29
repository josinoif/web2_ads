# Ferramentas para rodar scripts .sh dos labs no Windows (e em qualquer host sem bash).
# Imagem: aulas-ads-lab-tools
FROM docker:27-cli AS dockercli
RUN mkdir -p /export \
    && cp /usr/local/bin/docker /export/docker \
    && (cp /usr/local/libexec/docker/cli-plugins/docker-compose /export/docker-compose \
        || cp /usr/libexec/docker/cli-plugins/docker-compose /export/docker-compose)

FROM python:3.12-slim-bookworm

COPY --from=dockercli /export/docker /usr/local/bin/docker
COPY --from=dockercli /export/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash curl ca-certificates wget \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /usr/libexec/docker/cli-plugins \
    && ln -sf /usr/local/libexec/docker/cli-plugins/docker-compose /usr/libexec/docker/cli-plugins/docker-compose \
    && chmod +x /usr/local/bin/docker /usr/local/libexec/docker/cli-plugins/docker-compose

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

WORKDIR /work
ENTRYPOINT ["/entrypoint.sh"]
