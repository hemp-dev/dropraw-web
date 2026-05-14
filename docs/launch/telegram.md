# Telegram

DropRaw Web v0.1.0 готов к open-source релизу.

Это CLI + локальный UI для конвертации больших RAW-папок из Dropbox, Google Drive, S3/R2 и local folders в WebP/AVIF/JPEG/PNG.

Ключевая идея: не скачивать огромный ZIP. Файлы обрабатываются по одному, с retry, `.part` downloads, failed log, resume и reports.
