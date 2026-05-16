# RawBridge

English | [Русский](README.ru.md) | [Español](README.es.md) | [中文](README.zh.md) | [Deutsch](README.de.md) | [Français](README.fr.md)

Local-first RAW archive pipeline for turning cloud folders into web-ready images — without broken ZIP downloads.

<!-- Badges are intentionally conservative until public services are connected.
TODO: tests badge after GitHub repo is public.
TODO: PyPI badge after rawbridge is published.
TODO: GHCR/Docker badge after container image is published.
-->

## What It Does

RawBridge is an open-source CLI and local UI for turning large RAW photo folders into optimized web-ready image assets.

It processes large RAW photo folders from Dropbox, Google Drive, S3/R2, MinIO, or local directories one file at a time, with retries, resumable state, privacy-safe metadata handling, and ready-to-use WebP/AVIF/JPEG/PNG outputs.

It is built for photographers, designers, agencies, developers, and content teams who need reliable web assets from heavy RAW archives without manually downloading huge ZIP files.

## Why RawBridge?

Cloud photo folders often break when exported as huge ZIP archives. RawBridge avoids that fragile workflow.

Instead of downloading everything at once, it:

- scans the source folder;
- downloads files one by one;
- keeps a resumable SQLite manifest;
- retries transient network errors;
- writes failed items to a log;
- converts RAW files to web-ready formats;
- optionally strips sensitive EXIF/GPS metadata;
- generates outputs ready for websites, CMS, previews, and catalogs.

## Search Summary

RawBridge is a multi-cloud RAW photo conversion tool for photographers, designers, agencies, and web developers who need to export large RAW folders into web-ready WebP, AVIF, JPEG, or PNG assets. It is useful when Dropbox folder ZIP downloads fail, when Google Drive or S3/R2 assets need batch conversion, or when a local RAW archive must be prepared for a website, CMS, gallery, or design handoff.

## Tested On A Real Dropbox RAW Folder

RawBridge was tested on a real Dropbox shared folder with 816 Nikon NEF files.

Large Dropbox folders may fail during listing or download due to transient network, SSL, or SDK errors. RawBridge handles this with listing retries, download retries, exponential backoff, `.part` downloads, size checks, a failed log, retry only failed, and resume without overwriting existing outputs.

The recoverable error `ConnectionError(ProtocolError('Connection aborted.', OSError(22, 'Invalid argument')))` is treated as a transient network error. A file that succeeds after retry is counted as processed, not failed.

## Key Features

- CLI and local web UI.
- Local folder, Dropbox shared folder, Google Drive, S3, Cloudflare R2, and MinIO sources.
- Dropbox shared folder conversion without ZIP download.
- WebP, AVIF, JPEG, and PNG outputs.
- Responsive image variants and `<picture>` snippets.
- SQLite manifest and resume support.
- Listing retries, download retries, exponential backoff, cooldown, and `.part` downloads.
- Failed log and `--only-failed`.
- JSON, CSV, HTML, assets, errors, and failed-file reports.
- Metadata privacy modes with GPS stripping recommended by default.
- Docker and docker-compose support.

## Supported Sources

- `local`: local folders.
- `dropbox`: Dropbox shared folders.
- `google-drive`: Google Drive folders.
- `s3`: AWS S3 buckets and compatible storage.
- `r2`: Cloudflare R2 with `--endpoint-url`.
- `minio`: S3-compatible MinIO with an endpoint URL.
- `onedrive`, `yadisk`, `box`: roadmap or experimental provider skeletons unless marked otherwise by tests.

## Supported RAW Formats

NEF, NRW, CR2, CR3, ARW, RAF, RW2, ORF, DNG, PEF, RAW, RWL, IIQ, 3FR, ERF, MEF, MOS, MRW, SRW, X3F.

## Supported Output Formats

WebP, AVIF, JPEG, and PNG. AVIF availability depends on the installed Pillow build.

## Installation

Recommended Python versions: 3.11 and 3.12.

Python 3.14 is not recommended for this release because imaging and networking dependencies may lag behind it.

```bash
pip install rawbridge
```

Development install:

```bash
git clone https://github.com/hemp-dev/rawbridge.git
cd rawbridge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

```bash
rawbridge --version
rawbridge doctor
rawbridge scan ./RAW
rawbridge convert ./RAW --out ./web_export --preset web
```

## Dropbox Example

```bash
rawbridge convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --preset web \
  --list-retries 10 \
  --download-retries 10 \
  --retry-delay 3 \
  --cooldown 1
```

Retry only failed files:

```bash
rawbridge convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/rawbridge_failed.tsv
```

## Google Drive Example

```bash
rawbridge convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

Google Drive may require a service account or API key depending on folder visibility.

## S3/R2 Example

```bash
rawbridge convert s3://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Cloudflare R2:

```bash
rawbridge convert r2://bucket/raw \
  --endpoint-url https://ACCOUNT_ID.r2.cloudflarestorage.com \
  --out ./web_export \
  --preset web
```

## Local Folder Example

```bash
rawbridge scan ./RAW
rawbridge convert ./RAW --provider local --out ./web_export --preset web
```

## UI Mode

```bash
rawbridge ui
```

Open `http://127.0.0.1:8787`. The UI supports source setup, scan, conversion settings, retry settings, progress, failed files, reports, and Doctor checks.

## Retry, Failed Log, And Resume

Every conversion writes `.rawbridge_manifest.sqlite` in the output directory. Existing outputs are skipped unless `--overwrite` is enabled.

Failed files are written to `rawbridge_failed.tsv`. Use `--only-failed ./web_export/rawbridge_failed.tsv` to retry just those paths.

## Metadata Privacy

Default metadata mode is `strip`. It is recommended for public websites and removes GPS/private camera data where encoders support it.

Modes:

- `strip`: remove EXIF/GPS where possible.
- `keep-color`: keep color profile data where possible, remove GPS/private metadata.
- `keep-all`: preserve as much metadata as encoder support allows.

Never put Dropbox tokens, Google credentials, AWS secrets, OAuth refresh tokens, Git hosting tokens, or CI secrets in issues, logs, reports, docs, or mirror scripts.

## Reports

RawBridge can generate:

- `report.json`
- `report.csv`
- `errors.csv`
- `assets.json`
- `report.html`
- `picture-snippets.html`
- `rawbridge_failed.tsv`

## Docker

```bash
docker build -t rawbridge:0.1.0 .
docker run --rm \
  -v "$PWD/output:/output" \
  -e DROPBOX_ACCESS_TOKEN="..." \
  rawbridge:0.1.0 \
  rawbridge convert "DROPBOX_LINK" --provider dropbox --out /output
```

Published image names:

```bash
docker pull ghcr.io/hemp-dev/rawbridge:0.1.0
docker pull ghcr.io/hemp-dev/rawbridge:latest
```

## International Mirrors

GitHub is the primary repository unless maintainers change that. GitLab, Codeberg, and Bitbucket are primary international mirrors. See [MIRRORS.md](MIRRORS.md).

## Russian Mirrors

GitFlic is the recommended main Russian public mirror. GitVerse is the recommended secondary Russian public/private mirror. See [RUSSIAN_MIRRORS.md](RUSSIAN_MIRRORS.md).

## Self-hosted Deployment

Forgejo, Gitea, and Сфера.Код / Платформа Сфера are documented as self-hosted or enterprise DevOps targets. Do not claim an active mirror until remotes and CI are verified.

## Troubleshooting

- Run `rawbridge doctor`.
- Use Python 3.11 or 3.12.
- Increase `--list-retries`, `--download-retries`, and `--retry-delay` for large cloud folders.
- Use `--only-failed` after interrupted or partially failed runs.
- Check AVIF support with `rawbridge doctor`.
- Keep credentials in environment variables or local secret stores, not committed files.

## FAQ

### What is RawBridge?

RawBridge is an open-source CLI and local UI for converting large RAW photo folders from Dropbox, Google Drive, S3/R2, and local folders into optimized WebP, AVIF, JPEG, and PNG assets.

### Does RawBridge download Dropbox folders as ZIP files?

No. RawBridge scans Dropbox shared folders through provider listing and downloads RAW files one by one. This makes retries, `.part` downloads, failed logs, and resume practical for large folders.

### Who is RawBridge for?

RawBridge is for photographers, designers, creative agencies, web developers, and teams that need to prepare RAW photo archives for websites, CMS uploads, galleries, landing pages, or asset pipelines.

### Which Python versions are recommended?

Python 3.11 and Python 3.12 are recommended for RawBridge v0.1.x. Python 3.14 is not recommended yet.

### Can RawBridge resume after a failed cloud download?

Yes. RawBridge uses a SQLite manifest, `.part` downloads, retry settings, failed logs, and `--only-failed` so interrupted jobs can continue without overwriting existing outputs.

### Does RawBridge remove photo metadata?

The default metadata mode is `strip`, which removes GPS and private camera metadata where supported by the output encoder. This is recommended for public websites.

## Compatibility

RawBridge was formerly named DropRaw Web.

New usage should prefer:

```bash
rawbridge ...
```

The `dropraw` command remains available as a legacy alias.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Provider contributions should implement the `StorageProvider` interface, avoid whole-folder archive downloads when API listing is possible, and include tests and docs.

## License

MIT. See [LICENSE](LICENSE).
