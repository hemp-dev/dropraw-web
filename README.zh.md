# RawBridge

[English](README.md) | [Русский](README.ru.md) |
[Español](README.es.md) | 中文 | [Deutsch](README.de.md) |
[Français](README.fr.md)

RawBridge 可以把 Dropbox、Google Drive、S3 兼容存储和本地磁盘中的大型
RAW 照片目录转换成可直接用于网站的图片资源。

它不依赖“把整个文件夹下载成一个巨大 ZIP”的脆弱流程。RawBridge 会列出
源目录，逐个下载 RAW 文件，转换图片，把进度写入本地 manifest，并允许你
在网络错误或处理失败后继续运行。

## 项目状态

RawBridge 目前是早期 open-source 版本。Python 包名是 `rawbridge`，主要
CLI 命令也是 `rawbridge`。

推荐使用 Python 3.11 或 3.12。本版本线不支持 Python 3.14，因为图片处理和
云 SDK 依赖可能还没有完全跟上。

## 适用场景

当你需要完成这些工作时，可以使用 RawBridge：

- 把 Dropbox shared folder 中的 RAW 文件转换成 WebP/JPEG，而不再依赖容易
  失败的 ZIP 导出；
- 为网站、CMS、目录、图库或设计交付准备本地 RAW 归档；
- 把 Google Drive、S3、R2 或 MinIO 文件夹转换成结构可预测的输出文件；
- 在长时间云端任务失败后，只重试失败的文件；
- 为网页发布生成报告和 `<picture>` 代码片段；
- 在公开图片前移除 GPS 和私有相机元数据。

## 功能

- CLI 和本地 web UI。
- 支持本地文件夹和 Dropbox shared link。
- 实验性支持 Google Drive 和 S3/R2/MinIO。
- 输出 WebP、AVIF、JPEG 和 PNG。
- 提供 web、preview、retina、Tilda、WordPress 和 lossless web export
  presets。
- 生成 `image@1200.webp` 这样的 responsive variants。
- 在输出目录中使用 SQLite manifest 支持 resume。
- 失败日志和 `--only-failed` 重试。
- Listing retries、download retries、exponential backoff、cooldown、`.part`
  downloads 和文件大小校验。
- JSON、CSV、HTML、assets、errors 和 picture snippets 报告。
- 元数据隐私模式：`strip`、`keep-color` 和 `keep-all`。
- 支持 Docker 和 docker-compose。

## 支持的来源

| Provider | 状态 | Source 示例 |
| --- | --- | --- |
| `local` | 稳定 | `./RAW` |
| `dropbox` | 稳定 | `https://www.dropbox.com/scl/fo/...` |
| `google-drive` | 实验性 | `https://drive.google.com/drive/folders/FOLDER_ID` |
| `s3` | 实验性 | `s3://bucket/raw` |
| `r2` | 通过 S3 provider 实验性支持 | `r2://bucket/raw` |
| `minio` | 通过 S3 provider 实验性支持 | `minio://bucket/raw` |
| `onedrive` | 计划中 | 只有 provider skeleton |
| `yadisk` | 计划中 | 只有 provider skeleton |
| `box` | 计划中 | 只有 provider skeleton |

支持的 RAW 扩展名包括 `NEF`、`NRW`、`CR2`、`CR3`、`ARW`、`RAF`、`RW2`、
`ORF`、`DNG`、`PEF`、`RAW`、`RWL`、`IIQ`、`3FR`、`ERF`、`MEF`、`MOS`、
`MRW`、`SRW` 和 `X3F`。

AVIF 输出取决于已安装 Pillow 是否带有 AVIF 支持。请运行
`rawbridge doctor` 检查环境。

## 安装

用于本地开发，或直接从这个仓库运行：

```bash
git clone https://github.com/hemp-dev/rawbridge.git
cd rawbridge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

当包已经发布到你的 package index 后，可以这样安装：

```bash
pip install rawbridge
```

## 快速开始

```bash
rawbridge --version
rawbridge doctor
rawbridge scan ./RAW
rawbridge convert ./RAW --out ./web_export --preset web
```

默认 `web` preset 会写出 WebP 和 JPEG，把最长边限制到 2560 px，使用
quality `88`，并移除元数据。

## Dropbox

在 shell 或本地 `.env` 文件中设置 Dropbox token：

```bash
export DROPBOX_ACCESS_TOKEN="..."
```

转换 shared folder：

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

RawBridge 已在一个真实 Dropbox shared folder 上测试，该目录包含 816 个
Nikon NEF 文件。临时的 Dropbox、SSL 和网络错误会被重试。如果文件在 retry
后成功处理，它会被计为 processed，而不是 failed。

只重试失败文件：

```bash
rawbridge convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/rawbridge_failed.tsv
```

## Google Drive

Google Drive 需要 service account 文件或 API key：

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
# 或
export GOOGLE_API_KEY="..."
```

然后运行：

```bash
rawbridge convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

如果使用 service account，请确保 Drive 文件夹已经共享给该 service account
的 email。

## S3、Cloudflare R2 和 MinIO

AWS S3 使用标准 AWS 环境变量：

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"

rawbridge convert s3://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Cloudflare R2 和 MinIO 需要 S3-compatible endpoint：

```bash
export AWS_ENDPOINT_URL="https://ACCOUNT_ID.r2.cloudflarestorage.com"

rawbridge convert r2://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

也可以使用 `S3_ENDPOINT_URL` 代替 `AWS_ENDPOINT_URL`。

## 本地 web UI

启动本地 UI：

```bash
rawbridge ui
```

打开 `http://127.0.0.1:8787`。UI 支持 source setup、scan、conversion
settings、retry settings、progress、failed files、reports 和 Doctor checks。

在受限环境中，可以配置允许访问的根目录：

```bash
export RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS="/input"
export RAWBRIDGE_UI_ALLOWED_OUTPUT_ROOTS="/output"
```

## Presets

| Preset | 输出 | 典型用途 |
| --- | --- | --- |
| `web` | WebP + JPEG, max 2560 px | 常规网站图片 |
| `preview` | WebP, max 1600 px, half-size decode | 快速预览 |
| `retina` | WebP + JPEG responsive sizes | 高像素密度屏幕 |
| `lossless_web` | Lossless WebP + PNG | 归档型 web export |
| `tilda` | WebP + JPEG responsive sizes | Tilda 发布 |
| `wordpress` | WebP + JPEG responsive sizes | WordPress media sizes |

需要时可以从 CLI 覆盖 preset：

```bash
rawbridge convert ./RAW \
  --out ./web_export \
  --preset wordpress \
  --format webp,jpg \
  --responsive-sizes 768,1200,1536,2048 \
  --quality 86
```

## Resume、失败文件和清理

每次转换都会在输出目录写入 `.rawbridge_manifest.sqlite`。启用 resume 时，
已有输出文件默认会被跳过。

失败路径会写入 `rawbridge_failed.tsv`。修复 credentials、网络访问或问题 RAW
文件后，可以用 `--only-failed` 只重试这些文件。

常用命令：

```bash
rawbridge resume JOB_ID
rawbridge report JOB_ID
rawbridge clean --out ./web_export
```

## 报告

RawBridge 会在输出目录写入这些文件：

- `report.json`
- `report.csv`
- `errors.csv`
- `assets.json`
- `report.html`
- `picture-snippets.html`
- `rawbridge_failed.tsv`

CSV 报告会防护 spreadsheet formula injection。HTML snippets 在写入前会转义
文件路径。

## 元数据隐私

默认模式是 `strip`。在 encoder 支持的情况下，它会移除 EXIF/GPS/私有相机
数据。需要保留色彩配置但移除私有元数据时，使用 `keep-color`。`keep-all`
只适合可信、非公开流程。

不要把 Dropbox tokens、Google credentials、AWS secrets、OAuth refresh
tokens、Git hosting tokens 或 CI secrets 发布到 issues、logs、reports、docs
或 mirror scripts 中。

## Docker

构建本地 image：

```bash
docker build -t rawbridge:0.1.0 .
```

运行转换：

```bash
docker run --rm \
  -v "$PWD/RAW:/input:ro" \
  -v "$PWD/web_export:/output" \
  rawbridge:0.1.0 \
  rawbridge convert /input --provider local --out /output --preset web
```

对于云 provider，请通过环境变量传递 credentials，不要把它们写进 image。

## 文档

可以从这里开始：

- [中文文档](docs/zh/index.md)
- [快速开始](docs/zh/quick-start.md)
- [安装](docs/zh/installation.md)
- [Mirrors](MIRRORS.md)
- [Russian mirrors](RUSSIAN_MIRRORS.md)

## 开发

运行测试：

```bash
pytest
```

构建文档：

```bash
./scripts/build_docs.sh
```

运行 smoke test：

```bash
./scripts/smoke_test.sh
```

## 贡献

请查看 [CONTRIBUTING.md](CONTRIBUTING.md)、[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)、
[SECURITY.md](SECURITY.md) 和 [ROADMAP.md](ROADMAP.md)。

## 许可证

MIT。请查看 [LICENSE](LICENSE)。
