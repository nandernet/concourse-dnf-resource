FROM quay.io/fedora/fedora-minimal:latest AS base

LABEL org.opencontainers.image.authors='Nic Anderson <docker@nic-a.net>' \
      org.opencontainers.image.url='https://github.com/nanderson94/concourse-dnf-resource' \
      org.opencontainers.image.documentation='https://github.com/nanderson94/concourse-dnf-resource' \
      org.opencontainers.image.source='https://github.com/nanderson94/concourse-dnf-resource' \
      org.opencontainers.image.licenses='Apache-2.0'

#RUN \
#      microdnf -y update && \
#      microdnf -y clean all && \



