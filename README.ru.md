# DropRaw Web

[English](README.md) | Русский | [Español](README.es.md) | [中文](README.zh.md) | [Deutsch](README.de.md) | [Français](README.fr.md)

Конвертация больших RAW-папок из Dropbox, Google Drive, S3/R2 и локальных папок в оптимизированные WebP/AVIF/JPEG без скачивания огромных ZIP-архивов.

<!-- TODO badges: tests, PyPI, Docker/GHCR после публикации публичных сервисов. -->

## Что делает проект

DropRaw Web — open-source CLI и локальный UI-инструмент для подготовки больших RAW-фотоархивов к публикации на сайте.

Он умеет сканировать Dropbox shared folders, Google Drive folders, S3/R2 buckets и локальные папки, скачивать RAW-файлы по одному, конвертировать их в WebP/AVIF/JPEG/PNG и безопасно продолжать работу после сетевых сбоев.

Он не скачивает огромные ZIP-архивы папок.

## Почему не ZIP

Большие ZIP-скачивания из облаков часто обрываются. DropRaw Web работает через listing API, скачивает файлы по одному, пишет `.part` файлы, проверяет размер, ведет failed log и умеет retry только failed-файлов.

## Tested on a real Dropbox RAW folder

Проект проверен на реальной Dropbox shared folder с 816 Nikon NEF files. Большие Dropbox folders могут падать при listing или download из-за временных network/SSL/SDK ошибок.

DropRaw Web использует listing retries, download retries, exponential backoff, `.part` downloads, size checks, failed log, retry only failed и resume без перезаписи готовых outputs.

Ошибка `ConnectionError(ProtocolError('Connection aborted.', OSError(22, 'Invalid argument')))` считается временной сетевой ошибкой. Если файл успешно скачался после retry, он считается обработанным, а не failed.

## Key features

- CLI и локальный web UI.
- Local, Dropbox, Google Drive, S3/R2 и MinIO sources.
- Dropbox shared folder без ZIP-download.
- WebP, AVIF, JPEG, PNG outputs.
- SQLite manifest, resume, failed log, `--only-failed`.
- Retry/backoff/cooldown и `.part` downloads.
- Reports: JSON, CSV, HTML, assets, errors.
- Metadata privacy modes.
- Docker и docker-compose.

## Supported sources

`local`, `dropbox`, `google-drive`, `s3`, `r2`, `minio`. `onedrive`, `yadisk`, `box` пока roadmap/experimental, если не указано иначе.

## Supported RAW formats

NEF, NRW, CR2, CR3, ARW, RAF, RW2, ORF, DNG, PEF, RAW, RWL, IIQ, 3FR, ERF, MEF, MOS, MRW, SRW, X3F.

## Supported output formats

WebP, AVIF, JPEG, PNG. AVIF зависит от Pillow build.

## Installation

Рекомендуемые версии Python: 3.11 и 3.12. Python 3.14 пока не recommended.

```bash
pip install dropraw-web
```

Dev install:

```bash
git clone https://github.com/hemp-dev/dropraw-web.git
cd dropraw-web
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```bash
dropraw --version
dropraw doctor
dropraw scan ./RAW
dropraw convert ./RAW --out ./web_export --preset web
```

## Dropbox example

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

Retry failed:

```bash
dropraw convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/dropraw_failed.tsv
```

## Google Drive example

```bash
dropraw convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

## S3/R2 example

```bash
dropraw convert s3://bucket/raw --provider s3 --out ./web_export --preset web
dropraw convert r2://bucket/raw --endpoint-url https://ACCOUNT_ID.r2.cloudflarestorage.com --out ./web_export --preset web
```

## Local folder example

```bash
dropraw scan ./RAW
dropraw convert ./RAW --provider local --out ./web_export --preset web
```

## UI mode

```bash
dropraw ui
```

Откройте `http://127.0.0.1:8787`.

## Retry / failed log / resume

Manifest хранится в `.dropraw_manifest.sqlite`. Failed files пишутся в `dropraw_failed.tsv`. Для повторной обработки используйте `--only-failed`.

## Metadata privacy

Default mode: `strip`. Он удаляет GPS/private camera data, где это поддерживает encoder. Не публикуйте токены и credentials в issues, logs, reports или mirror scripts.

## Reports

`report.json`, `report.csv`, `errors.csv`, `assets.json`, `report.html`, `picture-snippets.html`, `dropraw_failed.tsv`.

## Docker

```bash
docker build -t dropraw-web:0.1.0 .
docker run --rm -v "$PWD/output:/output" -e DROPBOX_ACCESS_TOKEN="..." dropraw-web:0.1.0 dropraw convert "DROPBOX_LINK" --provider dropbox --out /output
```

## International mirrors

Primary repository: GitHub. Mirrors: GitLab, Codeberg, Bitbucket. См. [MIRRORS.md](MIRRORS.md).

## Russian mirrors

Основной российский mirror: GitFlic. Второй mirror: GitVerse. Сфера.Код рассматривается как enterprise/self-hosted target. РТК-Феникс описан как secure supply-chain context, не как Git mirror. См. [RUSSIAN_MIRRORS.md](RUSSIAN_MIRRORS.md).

## Self-hosted deployment

Forgejo, Gitea и Сфера.Код можно использовать как self-hosted/enterprise контуры. CI зависит от конкретной инсталляции.

## Troubleshooting

Запустите `dropraw doctor`, используйте Python 3.11/3.12, увеличьте retry settings для больших папок, проверьте AVIF support и храните credentials вне репозитория.

## Roadmap

См. [ROADMAP.md](ROADMAP.md).

## Contributing

См. [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. См. [LICENSE](LICENSE).
