# Dropbox

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

DropRaw Web does not download a folder ZIP. It lists files and downloads RAW files one by one.

Retry failed:

```bash
dropraw convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/dropraw_failed.tsv
```
