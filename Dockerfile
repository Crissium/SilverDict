# Stage 1: Frontend Builder
FROM node:lts-alpine3.19@sha256:ef3f47741e161900ddd07addcaca7e76534a9205e4cd73b2ed091ba339004a75 as frontend-builder

WORKDIR /silverdict/client

# Copy only package.json and yarn.lock to leverage Docker cache layer
COPY ./client/package.json ./client/yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy the entire client directory
COPY client ./

# Build the frontend
RUN yarn build

# Stage 2: Production Environment
FROM alpine:3.19.1@sha256:15c46ced65c6abed6a27472a7904b04273e9a8091a5627badd6ff016ab073171

ARG VERSION="1.1.4"
ARG ENABLE_FULL_TEXT_SEARCH=""
ARG ENABLE_MORPHOLOGY_ANALYSIS=""
ARG ENABLE_CHINESE_CONVERSION=""

ENV HOST="0.0.0.0"
ENV PORT="2628"

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

LABEL org.opencontainers.image.title="SilverDict"
LABEL org.opencontainers.image.description="Web-Based Alternative to GoldenDict"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.authors="Yi Xing <blandilyte@gmail.com>"
LABEL org.opencontainers.image.url="https://crissium.github.io/SilverDict"
LABEL org.opencontainers.image.source="https://github.com/Crissium/SilverDict"
LABEL org.opencontainers.image.licenses="GPL-3.0-or-later"


WORKDIR /silverdict/server

RUN adduser -D silverdict

COPY --chown=silverdict:silverdict ./server/requirements.txt /silverdict/server/requirements.txt

# Install dependencies
RUN apk update && \
  apk add --no-cache python3 lzo py3-yaml ${ENABLE_FULL_TEXT_SEARCH:+xapian-bindings-python3 py3-lxml} ${ENABLE_MORPHOLOGY_ANALYSIS:+libhunspell} && \
  apk add --no-cache --virtual .build-deps python3-dev py3-pip gcc g++ lzo-dev ${ENABLE_MORPHOLOGY_ANALYSIS:+hunspell-dev} ${ENABLE_CHINESE_CONVERSION:+make cmake doxygen} && \
  python3 -m venv $VIRTUAL_ENV --system-site-packages && \
  pip install --no-cache-dir -r requirements.txt && \
  if [ "$ENABLE_MORPHOLOGY_ANALYSIS" = "true" ]; then \
    ln -s /usr/include/hunspell/* /usr/include/ && \
    ln -s /usr/lib/libhunspell-*.so /usr/lib/libhunspell.so && \
    pip install hunspell; \
  fi && \
  if [ "$ENABLE_CHINESE_CONVERSION" = "true" ]; then \
    wget https://github.com/BYVoid/OpenCC/archive/refs/tags/ver.1.1.7.tar.gz && \
    tar xzf ver.1.1.7.tar.gz && \
    cd OpenCC-ver.1.1.7 && \
    pip install wheel && \
    make python-build && \
    make python-install && \
    pip uninstall -y wheel && \
    cd .. && \
    rm -rf OpenCC-ver.1.1.7 ver.1.1.7.tar.gz; \
  fi && \
  apk del .build-deps

# Copy server and built frontend from the frontend-builder stage
COPY --chown=silverdict:silverdict ./server /silverdict/server
COPY --from=frontend-builder --chown=silverdict:silverdict /silverdict/client/build /silverdict/server/build

# Switch to non-root user
USER silverdict

# Expose the required port
EXPOSE "${PORT}/tcp"

# Entry point for the application
ENTRYPOINT python server.py "${HOST}:${PORT}"
