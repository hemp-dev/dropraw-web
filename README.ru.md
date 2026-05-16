# RawBridge

[English](README.md) | Русский | [Español](README.es.md) |
[中文](README.zh.md) | [Deutsch](README.de.md) |
[Français](README.fr.md)

RawBridge конвертирует большие папки с RAW-фотографиями из Dropbox,
Google Drive, S3-совместимых хранилищ и локального диска в изображения,
готовые для сайта.

Инструмент не полагается на хрупкую схему «скачать одну огромную ZIP-архивную
папку». Вместо этого он получает список файлов, скачивает RAW по одному,
конвертирует их, сохраняет прогресс в локальном манифесте и позволяет
продолжить работу после сетевых или файловых ошибок.

## Статус проекта

RawBridge находится на ранней open-source стадии. Текущий Python-пакет
называется `rawbridge`, основная CLI-команда тоже называется `rawbridge`.

Рекомендуемые версии Python: 3.11 и 3.12. Python 3.14 не входит в поддерживаемый
диапазон этой ветки, потому что библиотеки для RAW, изображений и облачных SDK
могут ещё отставать.

## Когда нужен RawBridge

Используйте RawBridge, если нужно:

- превратить Dropbox shared folder с RAW-файлами в WebP/JPEG без проблем с ZIP;
- подготовить локальный RAW-архив для сайта, CMS, каталога, галереи или передачи
  дизайнеру;
- конвертировать папки Google Drive, S3, R2 или MinIO в предсказуемую структуру
  output-файлов;
- повторно обработать только файлы, которые упали в длинной облачной задаче;
- получить отчёты и готовые `<picture>` snippets для публикации;
- удалить GPS и приватные camera metadata перед публикацией изображений.

## Возможности

- CLI и локальный web UI.
- Поддержка локальных папок и Dropbox shared links.
- Экспериментальная поддержка Google Drive и S3/R2/MinIO.
- Output в WebP, AVIF, JPEG и PNG.
- Пресеты для web, preview, retina, Tilda, WordPress и lossless web exports.
- Responsive-варианты вроде `image@1200.webp`.
- SQLite manifest для resume в output-директории.
- Failed log и повтор через `--only-failed`.
- Listing retries, download retries, exponential backoff, cooldown, `.part`
  downloads и проверка размера файла.
- Отчёты JSON, CSV, HTML, assets, errors и picture snippets.
- Режимы metadata privacy: `strip`, `keep-color`, `keep-all`.
- Docker и docker-compose.

## Поддерживаемые источники

| Provider | Статус | Пример source |
| --- | --- | --- |
| `local` | Stable | `./RAW` |
| `dropbox` | Stable | `https://www.dropbox.com/scl/fo/...` |
| `google-drive` | Experimental | `https://drive.google.com/drive/folders/FOLDER_ID` |
| `s3` | Experimental | `s3://bucket/raw` |
| `r2` | Experimental через S3 provider | `r2://bucket/raw` |
| `minio` | Experimental через S3 provider | `minio://bucket/raw` |
| `onedrive` | Coming soon | Только provider skeleton |
| `yadisk` | Coming soon | Только provider skeleton |
| `box` | Coming soon | Только provider skeleton |

Поддерживаемые RAW-расширения: `NEF`, `NRW`, `CR2`, `CR3`, `ARW`, `RAF`,
`RW2`, `ORF`, `DNG`, `PEF`, `RAW`, `RWL`, `IIQ`, `3FR`, `ERF`, `MEF`, `MOS`,
`MRW`, `SRW`, `X3F`.

AVIF зависит от того, собран ли установленный Pillow с поддержкой AVIF.
Проверьте окружение командой `rawbridge doctor`.

## Установка

Для локальной разработки или запуска из этого репозитория:

```bash
git clone https://github.com/hemp-dev/rawbridge.git
cd rawbridge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

После публикации пакета в вашем package index его можно будет установить так:

```bash
pip install rawbridge
```

## Быстрый старт

```bash
rawbridge --version
rawbridge doctor
rawbridge scan ./RAW
rawbridge convert ./RAW --out ./web_export --preset web
```

Пресет `web` по умолчанию пишет WebP и JPEG, ограничивает длинную сторону
размером 2560 px, использует quality `88` и удаляет metadata.

## Dropbox

Перед запуском задайте Dropbox token в shell или локальном `.env`:

```bash
export DROPBOX_ACCESS_TOKEN="..."
```

Конвертация shared folder:

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

RawBridge проверялся на реальной Dropbox shared folder с 816 Nikon NEF files.
Временные Dropbox, SSL и network errors ретраятся. Если файл успешно обработан
после retry, он считается processed, а не failed.

Повтор только failed-файлов:

```bash
rawbridge convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/rawbridge_failed.tsv
```

## Google Drive

Для Google Drive нужен service account file или API key:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
# или
export GOOGLE_API_KEY="..."
```

Запуск:

```bash
rawbridge convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

Если используется service account, папка в Google Drive должна быть расшарена
на email этого service account.

## S3, Cloudflare R2 и MinIO

Для AWS S3 используются стандартные AWS environment variables:

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"

rawbridge convert s3://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Cloudflare R2 и MinIO требуют S3-compatible endpoint:

```bash
export AWS_ENDPOINT_URL="https://ACCOUNT_ID.r2.cloudflarestorage.com"

rawbridge convert r2://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Вместо `AWS_ENDPOINT_URL` можно использовать `S3_ENDPOINT_URL`.

## Локальный web UI

Запуск:

```bash
rawbridge ui
```

Откройте `http://127.0.0.1:8787`. UI поддерживает настройку source, scan,
conversion settings, retry settings, progress, failed files, reports и Doctor
checks.

Для ограниченных окружений задайте разрешённые корни:

```bash
export RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS="/input"
export RAWBRIDGE_UI_ALLOWED_OUTPUT_ROOTS="/output"
```

## Пресеты

| Preset | Output | Когда использовать |
| --- | --- | --- |
| `web` | WebP + JPEG, max 2560 px | Обычные изображения для сайта |
| `preview` | WebP, max 1600 px, half-size decode | Быстрые preview |
| `retina` | WebP + JPEG responsive sizes | Экраны высокой плотности |
| `lossless_web` | Lossless WebP + PNG | Архивные web exports |
| `tilda` | WebP + JPEG responsive sizes | Публикация в Tilda |
| `wordpress` | WebP + JPEG responsive sizes | Размеры WordPress media |

Параметры пресета можно переопределить из CLI:

```bash
rawbridge convert ./RAW \
  --out ./web_export \
  --preset wordpress \
  --format webp,jpg \
  --responsive-sizes 768,1200,1536,2048 \
  --quality 86
```

## Resume, failed files и cleanup

Каждая конвертация пишет `.rawbridge_manifest.sqlite` в output-директорию.
Готовые output-файлы по умолчанию пропускаются, если resume включён.

Failed paths пишутся в `rawbridge_failed.tsv`. Используйте `--only-failed`,
чтобы повторить только эти файлы после исправления credentials, сети или
проблемного RAW-файла.

Полезные команды:

```bash
rawbridge resume JOB_ID
rawbridge report JOB_ID
rawbridge clean --out ./web_export
```

## Отчёты

RawBridge пишет в output-директорию:

- `report.json`
- `report.csv`
- `errors.csv`
- `assets.json`
- `report.html`
- `picture-snippets.html`
- `rawbridge_failed.tsv`

CSV защищены от spreadsheet formula injection. HTML snippets экранируют пути к
файлам перед записью.

## Metadata privacy

Режим по умолчанию — `strip`. Он удаляет EXIF/GPS/private camera data там, где
это поддерживает encoder. Используйте `keep-color`, если нужно сохранить color
profile, но убрать приватные metadata. Используйте `keep-all` только для
доверенных непубличных сценариев.

Не публикуйте Dropbox tokens, Google credentials, AWS secrets, OAuth refresh
tokens, Git hosting tokens или CI secrets в issues, logs, reports, docs или
mirror scripts.

## Docker

Сборка локального image:

```bash
docker build -t rawbridge:0.1.0 .
```

Запуск конвертации:

```bash
docker run --rm \
  -v "$PWD/RAW:/input:ro" \
  -v "$PWD/web_export:/output" \
  rawbridge:0.1.0 \
  rawbridge convert /input --provider local --out /output --preset web
```

Для cloud providers передавайте credentials через environment variables, не
вшивайте их в image.

## Документация

Начните с этих файлов:

- [Русская документация](docs/ru/index.md)
- [Быстрый старт](docs/ru/quick-start.md)
- [Установка](docs/ru/installation.md)
- [Retry и resume](docs/ru/retry-resume.md)
- [Troubleshooting](docs/ru/troubleshooting.md)
- [Mirrors](MIRRORS.md)
- [Russian mirrors](RUSSIAN_MIRRORS.md)

## Разработка

Тесты:

```bash
pytest
```

Сборка документации:

```bash
./scripts/build_docs.sh
```

Smoke test:

```bash
./scripts/smoke_test.sh
```

## Участие в разработке

См. [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md),
[SECURITY.md](SECURITY.md) и [ROADMAP.md](ROADMAP.md).

## Лицензия

MIT. См. [LICENSE](LICENSE).
