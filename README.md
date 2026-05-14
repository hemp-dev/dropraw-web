# DropRaw Web

English | [Русский](README.ru.md) | [Español](README.es.md) | [中文](README.zh.md) | [Deutsch](README.de.md) | [Français](README.fr.md)

Convert large RAW photo folders from Dropbox, Google Drive, S3/R2 and local folders into optimized WebP/AVIF/JPEG assets without downloading huge ZIP archives.

<!-- Badges are intentionally conservative until public services are connected.
TODO: tests badge after GitHub repo is public.
TODO: PyPI badge after dropraw-web is published.
TODO: GHCR/Docker badge after container image is published.
-->

## What It Does

DropRaw Web is an open-source CLI and local UI for turning large RAW photo folders into optimized web-ready image assets.

It can scan Dropbox shared folders, Google Drive folders, S3/R2 buckets and local directories, download RAW files one by one, convert them into WebP/AVIF/JPEG/PNG, and resume safely after network failures.

It does not download huge ZIP archives.

## Why Not ZIP?

Large Dropbox and cloud folders often fail as ZIP downloads, especially when they contain hundreds of RAW files. DropRaw Web lists files through provider APIs, downloads one file at a time, writes `.part` downloads, checks sizes, records failures, and can retry only failed files.

## Tested On A Real Dropbox RAW Folder

DropRaw Web was tested on a real Dropbox shared folder with 816 Nikon NEF files.

Large Dropbox folders may fail during listing or download due to transient network, SSL, or SDK errors. DropRaw Web handles this with listing retries, download retries, exponential backoff, `.part` downloads, size checks, a failed log, retry only failed, and resume without overwriting existing outputs.

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
pip install dropraw-web
```

Development install:

```bash
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

Retry only failed files:

```bash
dropraw convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/dropraw_failed.tsv
```

## Google Drive Example

```bash
dropraw convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

Google Drive may require a service account or API key depending on folder visibility.

## S3/R2 Example

```bash
dropraw convert s3://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Cloudflare R2:

```bash
dropraw convert r2://bucket/raw \
  --endpoint-url https://ACCOUNT_ID.r2.cloudflarestorage.com \
  --out ./web_export \
  --preset web
```

## Local Folder Example

```bash
dropraw scan ./RAW
dropraw convert ./RAW --provider local --out ./web_export --preset web
```

## UI Mode

```bash
dropraw ui
```

Open `http://127.0.0.1:8787`. The UI supports source setup, scan, conversion settings, retry settings, progress, failed files, reports, and Doctor checks.

## Retry, Failed Log, And Resume

Every conversion writes `.dropraw_manifest.sqlite` in the output directory. Existing outputs are skipped unless `--overwrite` is enabled.

Failed files are written to `dropraw_failed.tsv`. Use `--only-failed ./web_export/dropraw_failed.tsv` to retry just those paths.

## Metadata Privacy

Default metadata mode is `strip`. It is recommended for public websites and removes GPS/private camera data where encoders support it.

Modes:

- `strip`: remove EXIF/GPS where possible.
- `keep-color`: keep color profile data where possible, remove GPS/private metadata.
- `keep-all`: preserve as much metadata as encoder support allows.

Never put Dropbox tokens, Google credentials, AWS secrets, OAuth refresh tokens, Git hosting tokens, or CI secrets in issues, logs, reports, docs, or mirror scripts.

## Reports

DropRaw Web can generate:

- `report.json`
- `report.csv`
- `errors.csv`
- `assets.json`
- `report.html`
- `picture-snippets.html`
- `dropraw_failed.tsv`

## Docker

```bash
docker build -t dropraw-web:0.1.0 .
docker run --rm \
  -v "$PWD/output:/output" \
  -e DROPBOX_ACCESS_TOKEN="..." \
  dropraw-web:0.1.0 \
  dropraw convert "DROPBOX_LINK" --provider dropbox --out /output
```

The planned primary image names are `ghcr.io/hemp-dev/dropraw-web:0.1.0` and `ghcr.io/hemp-dev/dropraw-web:latest` after GHCR publishing is configured.

## International Mirrors

GitHub is the primary repository unless maintainers change that. GitLab, Codeberg, and Bitbucket are primary international mirrors. See [MIRRORS.md](MIRRORS.md).

## Russian Mirrors

GitFlic is the recommended main Russian public mirror. GitVerse is the recommended secondary Russian public/private mirror. See [RUSSIAN_MIRRORS.md](RUSSIAN_MIRRORS.md).

## Self-hosted Deployment

Forgejo, Gitea, and Сфера.Код / Платформа Сфера are documented as self-hosted or enterprise DevOps targets. Do not claim an active mirror until remotes and CI are verified.

## Troubleshooting

- Run `dropraw doctor`.
- Use Python 3.11 or 3.12.
- Increase `--list-retries`, `--download-retries`, and `--retry-delay` for large cloud folders.
- Use `--only-failed` after interrupted or partially failed runs.
- Check AVIF support with `dropraw doctor`.
- Keep credentials in environment variables or local secret stores, not committed files.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Provider contributions should implement the `StorageProvider` interface, avoid whole-folder archive downloads when API listing is possible, and include tests and docs.

## License

MIT. See [LICENSE](LICENSE).
