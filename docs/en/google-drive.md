# Google Drive

```bash
rawbridge convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

Google Drive access may require a service account or API key depending on folder visibility.
