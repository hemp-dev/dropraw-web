# RawBridge

English | [Русский](README.ru.md) | [Español](README.es.md) |
[中文](README.zh.md) | [Deutsch](README.de.md) |
[Français](README.fr.md)

RawBridge converts large RAW photo folders from Dropbox, Google Drive,
S3-compatible storage, and local disks into web-ready image assets.

It avoids the fragile "download one huge ZIP" workflow. Instead, it lists the
source folder, downloads RAW files one by one, converts them, records progress
in a local manifest, and lets you resume after network or processing failures.

## Project status

RawBridge is an early open-source release. The Python package is named
`rawbridge`, and the CLI command is `rawbridge`.

Recommended Python versions are 3.11 and 3.12. Python 3.14 is outside the
supported range for this release line because imaging and cloud SDK
dependencies may lag behind it.

## What RawBridge is for

Use RawBridge when you need to:

- turn a Dropbox shared folder of RAW files into WebP/JPEG assets without ZIP
  export failures;
- prepare a local RAW archive for a website, CMS, catalog, gallery, or design
  handoff;
- convert Google Drive or S3/R2/MinIO folders into predictable output files;
- retry only failed files after a long cloud job;
- generate reports and `<picture>` snippets for web publishing;
- strip GPS and private camera metadata before images go public.

## Features

- CLI and local web UI.
- Local folder and Dropbox shared-link support.
- Experimental Google Drive and S3/R2/MinIO support.
- WebP, AVIF, JPEG, and PNG outputs.
- Presets for web, previews, retina assets, Tilda, WordPress, and lossless web
  exports.
- Responsive output variants such as `image@1200.webp`.
- SQLite resume manifest in the output directory.
- Failed-file log with `--only-failed`.
- Listing retries, download retries, exponential backoff, cooldowns, `.part`
  downloads, and size checks.
- JSON, CSV, HTML, asset, error, and picture-snippet reports.
- Metadata privacy modes: `strip`, `keep-color`, and `keep-all`.
- Docker and docker-compose support.

## Supported sources

| Provider | Status | Source example |
| --- | --- | --- |
| `local` | Stable | `./RAW` |
| `dropbox` | Stable | `https://www.dropbox.com/scl/fo/...` |
| `google-drive` | Experimental | `https://drive.google.com/drive/folders/FOLDER_ID` |
| `s3` | Experimental | `s3://bucket/raw` |
| `r2` | Experimental through the S3 provider | `r2://bucket/raw` |
| `minio` | Experimental through the S3 provider | `minio://bucket/raw` |
| `onedrive` | Coming soon | Provider skeleton only |
| `yadisk` | Coming soon | Provider skeleton only |
| `box` | Coming soon | Provider skeleton only |

Supported RAW extensions include `NEF`, `NRW`, `CR2`, `CR3`, `ARW`, `RAF`,
`RW2`, `ORF`, `DNG`, `PEF`, `RAW`, `RWL`, `IIQ`, `3FR`, `ERF`, `MEF`, `MOS`,
`MRW`, `SRW`, and `X3F`.

AVIF output depends on AVIF support in the installed Pillow build. Run
`rawbridge doctor` to check your environment.

## Install

For local development or for running from this repository:

```bash
git clone https://github.com/hemp-dev/rawbridge.git
cd rawbridge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

After a package release is available from your package index, install it with:

```bash
pip install rawbridge
```

## Quick start

```bash
rawbridge --version
rawbridge doctor
rawbridge scan ./RAW
rawbridge convert ./RAW --out ./web_export --preset web
```

The default `web` preset writes WebP and JPEG files, limits the longest side to
2560 pixels, uses quality `88`, and strips metadata.

## Dropbox

Set a Dropbox token in your shell or in a local `.env` file:

```bash
export DROPBOX_ACCESS_TOKEN="..."
```

Convert a shared folder:

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

RawBridge has been tested against a real Dropbox shared folder containing 816
Nikon NEF files. Transient Dropbox, SSL, and network errors are retried. If a
file succeeds after retry, it is counted as processed, not failed.

Retry only failed files:

```bash
rawbridge convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/rawbridge_failed.tsv
```

## Google Drive

Google Drive requires either a service account file or an API key:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
# or
export GOOGLE_API_KEY="..."
```

Then run:

```bash
rawbridge convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

For service accounts, make sure the Drive folder is shared with the service
account email.

## S3, Cloudflare R2, and MinIO

AWS S3 uses the standard AWS environment variables:

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"

rawbridge convert s3://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Cloudflare R2 and MinIO require an S3-compatible endpoint:

```bash
export AWS_ENDPOINT_URL="https://ACCOUNT_ID.r2.cloudflarestorage.com"

rawbridge convert r2://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

You can also use `S3_ENDPOINT_URL` instead of `AWS_ENDPOINT_URL`.

## Local web UI

Start the local UI:

```bash
rawbridge ui
```

Open `http://127.0.0.1:8787`. The UI supports source setup, scan, conversion
settings, retry settings, progress, failed files, reports, and Doctor checks.

For restricted environments, configure allowed roots:

```bash
export RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS="/input"
export RAWBRIDGE_UI_ALLOWED_OUTPUT_ROOTS="/output"
```

## Presets

| Preset | Output | Typical use |
| --- | --- | --- |
| `web` | WebP + JPEG, max 2560 px | General website images |
| `preview` | WebP, max 1600 px, half-size decode | Fast previews |
| `retina` | WebP + JPEG responsive sizes | High-density screens |
| `lossless_web` | Lossless WebP + PNG | Archival web exports |
| `tilda` | WebP + JPEG responsive sizes | Tilda publishing |
| `wordpress` | WebP + JPEG responsive sizes | WordPress media sizes |

Override presets from the CLI when needed:

```bash
rawbridge convert ./RAW \
  --out ./web_export \
  --preset wordpress \
  --format webp,jpg \
  --responsive-sizes 768,1200,1536,2048 \
  --quality 86
```

## Resume, failed files, and cleanup

Each conversion writes `.rawbridge_manifest.sqlite` in the output directory.
Existing outputs are skipped by default when resume is enabled.

Failed paths are written to `rawbridge_failed.tsv`. Use `--only-failed` to
retry just those files after fixing credentials, network access, or a bad RAW
file.

Useful commands:

```bash
rawbridge resume JOB_ID
rawbridge report JOB_ID
rawbridge clean --out ./web_export
```

## Reports

RawBridge writes these files to the output directory:

- `report.json`
- `report.csv`
- `errors.csv`
- `assets.json`
- `report.html`
- `picture-snippets.html`
- `rawbridge_failed.tsv`

CSV reports are guarded against spreadsheet formula injection. HTML snippets
are escaped before writing file paths.

## Metadata privacy

The default metadata mode is `strip`. It removes EXIF/GPS/private camera data
where the encoder supports it. Use `keep-color` when you want to preserve color
profile information while still dropping private metadata. Use `keep-all` only
for trusted, non-public workflows.

Never put Dropbox tokens, Google credentials, AWS secrets, OAuth refresh tokens,
Git hosting tokens, or CI secrets in issues, logs, reports, docs, or mirror
scripts.

## Docker

Build the image locally:

```bash
docker build -t rawbridge:0.1.0 .
```

Run a conversion:

```bash
docker run --rm \
  -v "$PWD/RAW:/input:ro" \
  -v "$PWD/web_export:/output" \
  rawbridge:0.1.0 \
  rawbridge convert /input --provider local --out /output --preset web
```

For cloud providers, pass credentials through environment variables rather than
baking them into the image.

## Documentation

Start with:

- [English docs](docs/en/index.md)
- [Quick start](docs/en/quick-start.md)
- [Installation](docs/en/installation.md)
- [Retry and resume](docs/en/retry-resume.md)
- [Troubleshooting](docs/en/troubleshooting.md)
- [Mirrors](MIRRORS.md)
- [Russian mirrors](RUSSIAN_MIRRORS.md)

## Development

Run tests:

```bash
pytest
```

Build documentation:

```bash
./scripts/build_docs.sh
```

Run a smoke test:

```bash
./scripts/smoke_test.sh
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md),
[SECURITY.md](SECURITY.md), and [ROADMAP.md](ROADMAP.md).

## License

MIT. See [LICENSE](LICENSE).
