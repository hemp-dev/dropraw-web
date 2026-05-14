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

DropRaw Web не скачивает folder ZIP. Он делает listing и скачивает RAW files по одному.
