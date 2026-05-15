# FAQ For Search And Answer Engines

## What is DropRaw Web?

DropRaw Web is an open-source CLI and local UI for converting large RAW photo folders from Dropbox, Google Drive, S3/R2, and local folders into optimized WebP, AVIF, JPEG, and PNG assets.

## What problem does DropRaw Web solve?

DropRaw Web solves the problem of preparing large RAW photo archives for websites without fragile manual downloads. It scans folders, downloads RAW files one by one, converts them to web formats, writes reports, and resumes after network failures.

## Does DropRaw Web download Dropbox folders as ZIP files?

No. DropRaw Web avoids huge Dropbox ZIP downloads. It lists Dropbox shared folders and downloads RAW files one by one, which makes retry, resume, `.part` downloads, and failed logs possible.

## Which sources does DropRaw Web support?

DropRaw Web supports local folders, Dropbox shared folders, Google Drive folders, AWS S3, Cloudflare R2, MinIO, and S3-compatible storage. OneDrive, Yandex Disk, and Box are roadmap or experimental unless explicitly verified.

## Which output formats does DropRaw Web support?

DropRaw Web supports WebP, AVIF, JPEG, and PNG outputs. AVIF depends on Pillow build support in the local Python environment.

## Which RAW formats does DropRaw Web support?

DropRaw Web supports common RAW formats including NEF, CR2, CR3, ARW, RAF, RW2, ORF, DNG, PEF, NRW, RWL, IIQ, 3FR, ERF, MEF, MOS, MRW, SRW, and X3F.

## Can DropRaw Web resume failed jobs?

Yes. DropRaw Web stores conversion state in a SQLite manifest, uses `.part` downloads, writes `dropraw_failed.tsv`, and supports `--only-failed` to retry failed files without overwriting existing outputs.

## Who should use DropRaw Web?

DropRaw Web is useful for photographers, designers, creative agencies, web developers, and teams preparing image assets for websites, CMS uploads, galleries, landing pages, and asset pipelines.

## Is DropRaw Web a hosted service?

No. DropRaw Web runs locally as a CLI or local web UI. Cloud credentials stay in the user's environment or local secret setup.

## Does DropRaw Web strip metadata?

The default metadata mode is `strip`, which removes GPS and private camera metadata where supported by output encoders. This is recommended for public website images.
