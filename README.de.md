# RawBridge

[English](README.md) | [Русский](README.ru.md) |
[Español](README.es.md) | [中文](README.zh.md) | Deutsch |
[Français](README.fr.md)

RawBridge konvertiert große RAW-Fotoordner aus Dropbox, Google Drive,
S3-kompatiblem Storage und lokalen Laufwerken in webfertige Bilddateien.

Es vermeidet den anfälligen Ablauf, einen kompletten Ordner als riesiges ZIP zu
laden. RawBridge listet die Quelle, lädt RAW-Dateien einzeln herunter,
konvertiert sie, speichert den Fortschritt in einem lokalen Manifest und kann
nach Netzwerk- oder Verarbeitungsfehlern fortsetzen.

## Projektstatus

RawBridge ist eine frühe Open-Source-Version. Das Python-Paket heißt
`rawbridge`, und der wichtigste CLI-Befehl ist `rawbridge`.

Empfohlen sind Python 3.11 und 3.12. Python 3.14 liegt für diese Release-Linie
außerhalb des unterstützten Bereichs, weil Imaging- und Cloud-SDK-Abhängigkeiten
noch hinterherlaufen können.

## Wofür RawBridge gedacht ist

Nutzen Sie RawBridge, wenn Sie:

- einen Dropbox-Shared-Folder mit RAW-Dateien ohne ZIP-Exportfehler in WebP/JPEG
  umwandeln möchten;
- ein lokales RAW-Archiv für Website, CMS, Katalog, Galerie oder Design-Handoff
  vorbereiten müssen;
- Google-Drive-, S3-, R2- oder MinIO-Ordner in eine vorhersehbare
  Output-Struktur konvertieren möchten;
- nach einem langen Cloud-Job nur fehlgeschlagene Dateien erneut verarbeiten
  wollen;
- Reports und `<picture>`-Snippets für Web-Publishing benötigen;
- GPS- und private Kamerametadaten vor der Veröffentlichung entfernen möchten.

## Funktionen

- CLI und lokale Web UI.
- Unterstützung für lokale Ordner und Dropbox-Shared-Links.
- Experimentelle Unterstützung für Google Drive und S3/R2/MinIO.
- Ausgabe als WebP, AVIF, JPEG und PNG.
- Presets für Web, Previews, Retina, Tilda, WordPress und verlustfreie
  Web-Exports.
- Responsive Varianten wie `image@1200.webp`.
- SQLite-Manifest für Resume im Output-Verzeichnis.
- Failed-Log und erneute Verarbeitung mit `--only-failed`.
- Listing-Retries, Download-Retries, exponential backoff, Cooldowns, `.part`
  Downloads und Größenprüfung.
- Reports als JSON, CSV, HTML, Assets, Errors und Picture Snippets.
- Metadaten-Privacy-Modi: `strip`, `keep-color` und `keep-all`.
- Docker- und docker-compose-Unterstützung.

## Unterstützte Quellen

| Provider | Status | Source-Beispiel |
| --- | --- | --- |
| `local` | Stabil | `./RAW` |
| `dropbox` | Stabil | `https://www.dropbox.com/scl/fo/...` |
| `google-drive` | Experimentell | `https://drive.google.com/drive/folders/FOLDER_ID` |
| `s3` | Experimentell | `s3://bucket/raw` |
| `r2` | Experimentell über den S3-Provider | `r2://bucket/raw` |
| `minio` | Experimentell über den S3-Provider | `minio://bucket/raw` |
| `onedrive` | Geplant | Nur Provider-Skeleton |
| `yadisk` | Geplant | Nur Provider-Skeleton |
| `box` | Geplant | Nur Provider-Skeleton |

Unterstützte RAW-Erweiterungen sind `NEF`, `NRW`, `CR2`, `CR3`, `ARW`, `RAF`,
`RW2`, `ORF`, `DNG`, `PEF`, `RAW`, `RWL`, `IIQ`, `3FR`, `ERF`, `MEF`, `MOS`,
`MRW`, `SRW` und `X3F`.

AVIF-Ausgabe hängt davon ab, ob der installierte Pillow-Build AVIF unterstützt.
Prüfen Sie die Umgebung mit `rawbridge doctor`.

## Installation

Für lokale Entwicklung oder Ausführung aus diesem Repository:

```bash
git clone https://github.com/hemp-dev/rawbridge.git
cd rawbridge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Sobald das Paket in Ihrem Package Index verfügbar ist, installieren Sie es mit:

```bash
pip install rawbridge
```

## Schnellstart

```bash
rawbridge --version
rawbridge doctor
rawbridge scan ./RAW
rawbridge convert ./RAW --out ./web_export --preset web
```

Das Preset `web` schreibt WebP und JPEG, begrenzt die längste Seite auf
2560 px, verwendet quality `88` und entfernt Metadaten.

## Dropbox

Setzen Sie ein Dropbox-Token in der Shell oder in einer lokalen `.env`-Datei:

```bash
export DROPBOX_ACCESS_TOKEN="..."
```

Konvertieren Sie einen Shared Folder:

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

RawBridge wurde mit einem echten Dropbox-Shared-Folder mit 816 Nikon-NEF-Dateien
getestet. Temporäre Dropbox-, SSL- und Netzwerkfehler werden erneut versucht.
Wenn eine Datei nach einem Retry erfolgreich ist, zählt sie als verarbeitet und
nicht als fehlgeschlagen.

Nur fehlgeschlagene Dateien erneut versuchen:

```bash
rawbridge convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/rawbridge_failed.tsv
```

## Google Drive

Google Drive benötigt eine Service-Account-Datei oder einen API-Key:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
# oder
export GOOGLE_API_KEY="..."
```

Danach ausführen:

```bash
rawbridge convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

Bei Service Accounts muss der Drive-Ordner mit der E-Mail-Adresse des Service
Accounts geteilt sein.

## S3, Cloudflare R2 und MinIO

AWS S3 verwendet die Standard-AWS-Umgebungsvariablen:

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"

rawbridge convert s3://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Cloudflare R2 und MinIO benötigen einen S3-kompatiblen Endpoint:

```bash
export AWS_ENDPOINT_URL="https://ACCOUNT_ID.r2.cloudflarestorage.com"

rawbridge convert r2://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Sie können auch `S3_ENDPOINT_URL` statt `AWS_ENDPOINT_URL` verwenden.

## Lokale Web UI

Starten Sie die lokale UI:

```bash
rawbridge ui
```

Öffnen Sie `http://127.0.0.1:8787`. Die UI unterstützt Source-Setup, Scan,
Conversion Settings, Retry Settings, Progress, Failed Files, Reports und Doctor
Checks.

Für eingeschränkte Umgebungen konfigurieren Sie erlaubte Root-Verzeichnisse:

```bash
export RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS="/input"
export RAWBRIDGE_UI_ALLOWED_OUTPUT_ROOTS="/output"
```

## Presets

| Preset | Ausgabe | Typischer Einsatz |
| --- | --- | --- |
| `web` | WebP + JPEG, max 2560 px | Allgemeine Website-Bilder |
| `preview` | WebP, max 1600 px, half-size decode | Schnelle Previews |
| `retina` | WebP + JPEG responsive sizes | Displays mit hoher Pixeldichte |
| `lossless_web` | Verlustfreies WebP + PNG | Archiv-Web-Exports |
| `tilda` | WebP + JPEG responsive sizes | Tilda-Publishing |
| `wordpress` | WebP + JPEG responsive sizes | WordPress-Mediengrößen |

Presets lassen sich über die CLI überschreiben:

```bash
rawbridge convert ./RAW \
  --out ./web_export \
  --preset wordpress \
  --format webp,jpg \
  --responsive-sizes 768,1200,1536,2048 \
  --quality 86
```

## Resume, fehlgeschlagene Dateien und Cleanup

Jede Konvertierung schreibt `.rawbridge_manifest.sqlite` in das
Output-Verzeichnis. Existierende Outputs werden standardmäßig übersprungen,
wenn Resume aktiv ist.

Fehlgeschlagene Pfade werden in `rawbridge_failed.tsv` geschrieben. Verwenden
Sie `--only-failed`, um nur diese Dateien erneut zu versuchen, nachdem
Credentials, Netzwerkzugriff oder eine problematische RAW-Datei korrigiert
wurden.

Nützliche Befehle:

```bash
rawbridge resume JOB_ID
rawbridge report JOB_ID
rawbridge clean --out ./web_export
```

## Reports

RawBridge schreibt diese Dateien in das Output-Verzeichnis:

- `report.json`
- `report.csv`
- `errors.csv`
- `assets.json`
- `report.html`
- `picture-snippets.html`
- `rawbridge_failed.tsv`

CSV-Reports sind gegen spreadsheet formula injection abgesichert. HTML-Snippets
escapen Dateipfade vor dem Schreiben.

## Metadaten-Privacy

Der Standardmodus ist `strip`. Er entfernt EXIF/GPS/private Kameradaten, soweit
der Encoder das unterstützt. Verwenden Sie `keep-color`, wenn Farbprofile
erhalten bleiben sollen, private Metadaten aber entfernt werden sollen. Nutzen
Sie `keep-all` nur für vertrauenswürdige, nicht öffentliche Workflows.

Veröffentlichen Sie keine Dropbox-Tokens, Google-Credentials, AWS-Secrets,
OAuth-Refresh-Tokens, Git-Hosting-Tokens oder CI-Secrets in Issues, Logs,
Reports, Docs oder Mirror-Skripten.

## Docker

Lokales Image bauen:

```bash
docker build -t rawbridge:0.1.0 .
```

Konvertierung starten:

```bash
docker run --rm \
  -v "$PWD/RAW:/input:ro" \
  -v "$PWD/web_export:/output" \
  rawbridge:0.1.0 \
  rawbridge convert /input --provider local --out /output --preset web
```

Für Cloud-Provider sollten Credentials per Umgebungsvariable übergeben werden,
nicht im Image.

## Dokumentation

Starten Sie hier:

- [Deutsche Dokumentation](docs/de/index.md)
- [Schnellstart](docs/de/quick-start.md)
- [Installation](docs/de/installation.md)
- [Mirrors](MIRRORS.md)
- [Russian mirrors](RUSSIAN_MIRRORS.md)

## Entwicklung

Tests ausführen:

```bash
pytest
```

Dokumentation bauen:

```bash
./scripts/build_docs.sh
```

Smoke Test ausführen:

```bash
./scripts/smoke_test.sh
```

## Mitwirken

Siehe [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md),
[SECURITY.md](SECURITY.md) und [ROADMAP.md](ROADMAP.md).

## Lizenz

MIT. Siehe [LICENSE](LICENSE).
