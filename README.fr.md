# DropRaw Web

[English](README.md) | [Русский](README.ru.md) | [Español](README.es.md) | [中文](README.zh.md) | [Deutsch](README.de.md) | Français

Convertit de grands dossiers RAW depuis Dropbox, Google Drive, S3/R2 et des dossiers locaux en assets WebP/AVIF/JPEG optimisés, sans télécharger d'énormes archives ZIP.

<!-- TODO badges: tests, PyPI, Docker/GHCR after public publishing. -->

## What It Does

DropRaw Web est une CLI open-source avec local UI pour transformer de grands RAW photo folders en web-ready image assets. Il télécharge les RAW files un par un, convertit en WebP/AVIF/JPEG/PNG et reprend après les erreurs réseau.

## Why Not ZIP?

Les gros ZIP downloads échouent souvent. DropRaw Web utilise provider APIs, `.part` downloads, size checks, failed log, retry et resume.

## Tested on a real Dropbox RAW folder

Testé sur une vraie Dropbox shared folder avec 816 Nikon NEF files. `ConnectionError(ProtocolError('Connection aborted.', OSError(22, 'Invalid argument')))` est traité comme une erreur transitoire récupérable; un fichier réussi après retry est counted as processed, not failed.

## Key Features

CLI, local UI, Dropbox without ZIP-download, Google Drive, S3/R2, local folders, WebP/AVIF/JPEG/PNG, SQLite manifest, resume, failed log, `--only-failed`, reports, Docker, metadata privacy.

## Supported Sources

`local`, `dropbox`, `google-drive`, `s3`, `r2`, `minio`. `onedrive`, `yadisk`, `box` are roadmap/experimental unless documented otherwise.

## Supported RAW Formats

NEF, NRW, CR2, CR3, ARW, RAF, RW2, ORF, DNG, PEF, RAW, RWL, IIQ, 3FR, ERF, MEF, MOS, MRW, SRW, X3F.

## Supported Output Formats

WebP, AVIF, JPEG, PNG. AVIF depends on Pillow build support.

## Installation

Recommended Python versions: 3.11 and 3.12. Python 3.14 is not recommended yet.

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

## Dropbox / Google Drive / S3/R2 / Local

```bash
dropraw convert "https://www.dropbox.com/scl/fo/..." --provider dropbox --out ./web_export --preset web --list-retries 10 --download-retries 10 --retry-delay 3 --cooldown 1
dropraw convert "https://drive.google.com/drive/folders/FOLDER_ID" --provider google-drive --out ./web_export --preset web
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

See [MIRRORS.md](MIRRORS.md), [RUSSIAN_MIRRORS.md](RUSSIAN_MIRRORS.md), [ROADMAP.md](ROADMAP.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [LICENSE](LICENSE).
