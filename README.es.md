# DropRaw Web

[English](README.md) | [Русский](README.ru.md) | Español | [中文](README.zh.md) | [Deutsch](README.de.md) | [Français](README.fr.md)

Convierte grandes carpetas RAW desde Dropbox, Google Drive, S3/R2 y carpetas locales en assets WebP/AVIF/JPEG optimizados sin descargar enormes archivos ZIP.

<!-- TODO badges: tests, PyPI, Docker/GHCR after public publishing. -->

## Qué Hace

DropRaw Web es una CLI open-source y una UI local para preparar carpetas RAW grandes para la web. Escanea fuentes cloud/locales, descarga archivos RAW uno por uno, convierte a WebP/AVIF/JPEG/PNG y puede reanudar después de fallos de red.

## Por Qué No ZIP

Los ZIP grandes suelen fallar. DropRaw Web usa listing API, `.part` downloads, size checks, failed log, retry y resume.

## Tested on a real Dropbox RAW folder

Probado con una Dropbox shared folder real con 816 Nikon NEF files. Los errores transitorios como `ConnectionError(ProtocolError('Connection aborted.', OSError(22, 'Invalid argument')))` se tratan como recuperables; si un archivo funciona tras retry, cuenta como processed, no failed.

## Key Features

CLI, local UI, Dropbox sin ZIP-download, Google Drive, S3/R2, local folders, WebP/AVIF/JPEG/PNG, SQLite manifest, resume, failed log, `--only-failed`, reports, Docker, metadata privacy.

## Supported Sources

`local`, `dropbox`, `google-drive`, `s3`, `r2`, `minio`. `onedrive`, `yadisk`, `box` son roadmap/experimental salvo que se indique lo contrario.

## Supported RAW Formats

NEF, NRW, CR2, CR3, ARW, RAF, RW2, ORF, DNG, PEF, RAW, RWL, IIQ, 3FR, ERF, MEF, MOS, MRW, SRW, X3F.

## Supported Output Formats

WebP, AVIF, JPEG, PNG. AVIF depende del build de Pillow.

## Installation

Python recomendado: 3.11 o 3.12. Python 3.14 no se recomienda todavía.

```bash
pip install dropraw-web
git clone https://github.com/hemp-dev/dropraw-web.git
cd dropraw-web
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

```bash
dropraw --version
dropraw doctor
dropraw scan ./RAW
dropraw convert ./RAW --out ./web_export --preset web
```

## Dropbox Example

```bash
dropraw convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --preset web \
  --list-retries 10 \
  --download-retries 10 \
  --retry-delay 3 \
  --cooldown 1
```

## Google Drive Example

```bash
dropraw convert "https://drive.google.com/drive/folders/FOLDER_ID" --provider google-drive --out ./web_export --preset web
```

## S3/R2 And Local

```bash
dropraw convert s3://bucket/raw --provider s3 --out ./web_export --preset web
dropraw convert r2://bucket/raw --endpoint-url https://ACCOUNT_ID.r2.cloudflarestorage.com --out ./web_export --preset web
dropraw convert ./RAW --provider local --out ./web_export --preset web
```

## UI Mode

```bash
dropraw ui
```

## Retry / Failed Log / Resume

Use `dropraw_failed.tsv`, `.dropraw_manifest.sqlite`, and `--only-failed ./web_export/dropraw_failed.tsv`.

## Metadata Privacy, Reports, Docker, Mirrors

Default metadata mode is `strip`. Reports include `report.json`, `report.csv`, `report.html`, `assets.json`, `errors.csv`, and `picture-snippets.html`.

See [MIRRORS.md](MIRRORS.md) and [RUSSIAN_MIRRORS.md](RUSSIAN_MIRRORS.md). Build Docker with `docker build -t dropraw-web:0.1.0 .`.

## Roadmap / Contributing / License

See [ROADMAP.md](ROADMAP.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [LICENSE](LICENSE).
