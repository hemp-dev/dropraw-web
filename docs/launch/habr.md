# DropRaw Web: конвертация больших RAW-папок без огромных ZIP-архивов

DropRaw Web — open-source CLI и локальный UI для подготовки больших RAW-фотоархивов к публикации на сайте.

Практическая история началась с реальной Dropbox shared folder на 816 Nikon NEF files. Большие folders могут падать на listing/download из-за временных network/SSL/SDK ошибок, поэтому архитектура строилась вокруг retry/resume, `.part` downloads, failed log и отчетов.

Инструмент полезен фотографам, дизайнерам, агентствам и web developers, которым нужно надежно превратить RAW-архив в WebP/AVIF/JPEG assets без скачивания огромного ZIP.

Фокус релиза v0.1.0 — надежный MVP: Dropbox без ZIP-download, LocalProvider, Google Drive, S3/R2, SQLite manifest, reports, Docker, локальный UI и честная документация по international/Russian mirrors.
