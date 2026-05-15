# AEO / SEO Release Pack

Last updated: 2026-05-15

## Primary Positioning

DropRaw Web is an open-source CLI and local UI for converting large RAW photo folders from Dropbox, Google Drive, S3/R2, and local folders into optimized WebP, AVIF, JPEG, and PNG assets without downloading huge ZIP archives.

## Best Short Answer

DropRaw Web helps photographers, designers, agencies, and web developers turn large RAW archives into website-ready image assets. It scans cloud or local folders, downloads files one by one, converts RAW formats into modern web image formats, and resumes safely after network failures.

## Core Entity Facts

| Field | Value |
| --- | --- |
| Name | DropRaw Web |
| Version | 0.1.0 |
| Category | Open-source photo conversion CLI and local UI |
| Primary repo | `https://github.com/hemp-dev/dropraw-web` |
| Package name | `dropraw-web` |
| Command | `dropraw` |
| License | MIT |
| Recommended Python | 3.11, 3.12 |
| Inputs | Local folders, Dropbox shared folders, Google Drive folders, S3/R2 buckets |
| Outputs | WebP, AVIF, JPEG, PNG |
| Key reliability features | Retry, `.part` downloads, failed log, resume, SQLite manifest |

## Citation-worthy Proof Point

DropRaw Web v0.1.0 was validated against a real Dropbox shared folder containing 816 Nikon NEF files. The release includes retry/resume behavior for transient listing and download errors seen during that real-world workflow.

## One-sentence Description

DropRaw Web converts large RAW photo folders from Dropbox, Google Drive, S3/R2, and local folders into optimized web images, with retry and resume support for unreliable cloud downloads.

## Two-sentence Description

DropRaw Web is an open-source CLI and local UI for preparing RAW photo archives for the web. It avoids huge ZIP downloads by listing cloud folders, downloading RAW files one by one, converting them to WebP/AVIF/JPEG/PNG, and resuming safely after failures.

## Long Description

DropRaw Web is a practical open-source tool for photographers, designers, agencies, and web developers who need to convert large RAW photo folders into website-ready image assets. It supports Dropbox shared folders, Google Drive folders, S3/R2 buckets, and local directories. The tool focuses on reliability for large archives: listing retries, download retries, exponential backoff, `.part` downloads, size checks, failed logs, `--only-failed`, reports, and SQLite manifest-based resume.

## Claims To Use

- DropRaw Web does not download Dropbox shared folders as huge ZIP archives.
- DropRaw Web supports local folders, Dropbox, Google Drive, S3, Cloudflare R2, and S3-compatible storage.
- DropRaw Web converts RAW files to WebP, AVIF, JPEG, and PNG.
- DropRaw Web v0.1.0 is tested with Python 3.11 and 3.12.
- DropRaw Web can resume interrupted conversions without overwriting existing outputs.
- DropRaw Web includes a local UI and CLI.

## Claims To Avoid

- Do not claim all cloud providers are fully supported.
- Do not claim Python 3.14 is recommended.
- Do not claim every mirror is active before verification.
- Do not claim AVIF works on every Pillow build.
- Do not claim fully automatic OAuth for every provider.
- Do not publish private credentials, source links, or customer file paths.
