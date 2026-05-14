FROM node:22-slim AS ui-builder

WORKDIR /app/ui
COPY ui/package*.json ./
RUN npm install
COPY ui ./
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      build-essential \
      libraw-dev \
      libjpeg-dev \
      zlib1g-dev \
      libwebp-dev \
      libpng-dev \
      curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY configs ./configs
COPY src ./src
COPY --from=ui-builder /app/ui/dist ./ui/dist

RUN pip install --upgrade pip \
    && pip install . \
    && useradd --create-home --shell /usr/sbin/nologin dropraw \
    && chown -R dropraw:dropraw /app

EXPOSE 8787

USER dropraw

CMD ["dropraw", "--help"]
