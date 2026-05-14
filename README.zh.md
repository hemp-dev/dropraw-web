# DropRaw Web

[English](README.md) | [Русский](README.ru.md) | [Español](README.es.md) | 中文 | [Deutsch](README.de.md) | [Français](README.fr.md)

将 Dropbox、Google Drive、S3/R2 和本地文件夹中的大型 RAW 照片目录转换为优化后的 WebP/AVIF/JPEG 资源，无需下载巨大的 ZIP archives。

<!-- TODO badges: tests, PyPI, Docker/GHCR after public publishing. -->

## What It Does

DropRaw Web 是一个 open-source CLI 和 local UI，用于把大型 RAW photo folders 转成 web-ready image assets。它逐个下载 RAW files，转换为 WebP/AVIF/JPEG/PNG，并能在网络失败后 resume。

## Why Not ZIP?

大型 ZIP downloads 容易失败。DropRaw Web 使用 provider APIs listing、`.part` downloads、size checks、failed log、retry 和 resume。

## Tested on a real Dropbox RAW folder

已在真实 Dropbox shared folder 上测试，包含 816 Nikon NEF files。`ConnectionError(ProtocolError('Connection aborted.', OSError(22, 'Invalid argument')))` 被视为可恢复的 transient network error；retry 成功后文件计为 processed，而不是 failed。

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
