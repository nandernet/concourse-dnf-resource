FROM quay.io/fedora/fedora-minimal:latest AS base

ARG VER=0.1.0

LABEL org.opencontainers.image.authors='Nic Anderson <docker@nic-a.net>' \
      org.opencontainers.image.url='https://github.com/nanderson94/concourse-dnf-resource' \
      org.opencontainers.image.documentation='https://github.com/nanderson94/concourse-dnf-resource' \
      org.opencontainers.image.source='https://github.com/nanderson94/concourse-dnf-resource' \
      org.opencontainers.image.licenses='Apache-2.0'

RUN \
      microdnf -y update && \
      microdnf -y install python3-pip && \
      microdnf -y clean all

WORKDIR /app

FROM base as builder

RUN pip install poetry

COPY . .

RUN poetry build -n -C /app
RUN poetry export -f requirements.txt --without dev -o requirements.txt

FROM base

COPY --from=builder /app/requirements.txt /app
COPY --from=builder /app/dist/concourse_dnf-${VER}-py3-none-any.whl /app/dist/concourse_dnf-${VER}-py3-none-any.whl

# Hopefully one day we can do this to install the wheel:
# '--install-option="--install-scripts=/opt/resource/"'
# But for now, we symlink. See pypa/pip#3934
RUN \
      pip install -r /app/requirements.txt && \
      pip install /app/dist/concourse_dnf-${VER}-py3-none-any.whl && \
      mkdir -p /opt/resource && \
      ln -s /usr/local/bin/in /opt/resource/in && \
      ln -s /usr/local/bin/check /opt/resource/check && \
      ln -s /usr/local/bin/out /opt/resource/out

USER 1000

