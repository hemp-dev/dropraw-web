# RawBridge

[English](README.md) | [Русский](README.ru.md) | Español |
[中文](README.zh.md) | [Deutsch](README.de.md) |
[Français](README.fr.md)

RawBridge convierte carpetas grandes de fotos RAW desde Dropbox, Google Drive,
almacenamiento compatible con S3 y discos locales en imágenes listas para la
web.

Evita el flujo frágil de descargar una carpeta completa como un ZIP enorme.
RawBridge lista la fuente, descarga los RAW uno por uno, los convierte, guarda
el progreso en un manifiesto local y permite reanudar el trabajo después de
errores de red o de procesamiento.

## Estado del proyecto

RawBridge es una versión open-source temprana. El paquete de Python se llama
`rawbridge` y el comando principal de la CLI es `rawbridge`.

Las versiones recomendadas de Python son 3.11 y 3.12. Python 3.14 queda fuera
del rango soportado para esta línea de versión porque algunas dependencias de
imágenes y SDK de nube pueden tardar en ponerse al día.

## Para qué sirve RawBridge

Usa RawBridge cuando necesites:

- convertir una carpeta compartida de Dropbox con archivos RAW en WebP/JPEG sin
  fallos de exportación ZIP;
- preparar un archivo RAW local para un sitio web, CMS, catálogo, galería o
  entrega de diseño;
- convertir carpetas de Google Drive, S3, R2 o MinIO en una estructura de salida
  predecible;
- reintentar solo los archivos fallidos después de un trabajo largo en la nube;
- generar informes y fragmentos `<picture>` para publicación web;
- eliminar GPS y metadatos privados de cámara antes de publicar imágenes.

## Funciones

- CLI y web UI local.
- Soporte para carpetas locales y enlaces compartidos de Dropbox.
- Soporte experimental para Google Drive y S3/R2/MinIO.
- Salida en WebP, AVIF, JPEG y PNG.
- Presets para web, previews, retina, Tilda, WordPress y exportaciones web sin
  pérdida.
- Variantes responsive como `image@1200.webp`.
- Manifiesto SQLite para reanudar en el directorio de salida.
- Registro de fallos y reintento con `--only-failed`.
- Reintentos de listado y descarga, exponential backoff, cooldowns, descargas
  `.part` y verificación de tamaño.
- Informes JSON, CSV, HTML, assets, errores y picture snippets.
- Modos de privacidad de metadatos: `strip`, `keep-color` y `keep-all`.
- Soporte para Docker y docker-compose.

## Fuentes soportadas

| Provider | Estado | Ejemplo de source |
| --- | --- | --- |
| `local` | Estable | `./RAW` |
| `dropbox` | Estable | `https://www.dropbox.com/scl/fo/...` |
| `google-drive` | Experimental | `https://drive.google.com/drive/folders/FOLDER_ID` |
| `s3` | Experimental | `s3://bucket/raw` |
| `r2` | Experimental mediante el provider S3 | `r2://bucket/raw` |
| `minio` | Experimental mediante el provider S3 | `minio://bucket/raw` |
| `onedrive` | Próximamente | Solo esqueleto del provider |
| `yadisk` | Próximamente | Solo esqueleto del provider |
| `box` | Próximamente | Solo esqueleto del provider |

Las extensiones RAW soportadas incluyen `NEF`, `NRW`, `CR2`, `CR3`, `ARW`,
`RAF`, `RW2`, `ORF`, `DNG`, `PEF`, `RAW`, `RWL`, `IIQ`, `3FR`, `ERF`, `MEF`,
`MOS`, `MRW`, `SRW` y `X3F`.

La salida AVIF depende del soporte AVIF en la compilación instalada de Pillow.
Ejecuta `rawbridge doctor` para revisar el entorno.

## Instalación

Para desarrollo local o ejecución desde este repositorio:

```bash
git clone https://github.com/hemp-dev/rawbridge.git
cd rawbridge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Cuando el paquete esté disponible en tu package index, instálalo con:

```bash
pip install rawbridge
```

## Inicio rápido

```bash
rawbridge --version
rawbridge doctor
rawbridge scan ./RAW
rawbridge convert ./RAW --out ./web_export --preset web
```

El preset `web` escribe WebP y JPEG, limita el lado más largo a 2560 px, usa
quality `88` y elimina metadatos.

## Dropbox

Define un token de Dropbox en la shell o en un archivo local `.env`:

```bash
export DROPBOX_ACCESS_TOKEN="..."
```

Convierte una carpeta compartida:

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

RawBridge se probó con una carpeta compartida real de Dropbox que contenía 816
archivos Nikon NEF. Los errores transitorios de Dropbox, SSL y red se reintentan.
Si un archivo se procesa correctamente tras un reintento, cuenta como procesado,
no como fallido.

Reintenta solo los archivos fallidos:

```bash
rawbridge convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/rawbridge_failed.tsv
```

## Google Drive

Google Drive requiere un archivo de service account o una API key:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
# o
export GOOGLE_API_KEY="..."
```

Después ejecuta:

```bash
rawbridge convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

Si usas service account, comparte la carpeta de Drive con el correo de esa
cuenta.

## S3, Cloudflare R2 y MinIO

AWS S3 usa las variables de entorno estándar de AWS:

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"

rawbridge convert s3://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Cloudflare R2 y MinIO requieren un endpoint compatible con S3:

```bash
export AWS_ENDPOINT_URL="https://ACCOUNT_ID.r2.cloudflarestorage.com"

rawbridge convert r2://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

También puedes usar `S3_ENDPOINT_URL` en lugar de `AWS_ENDPOINT_URL`.

## Web UI local

Inicia la UI local:

```bash
rawbridge ui
```

Abre `http://127.0.0.1:8787`. La UI permite configurar la fuente, escanear,
ajustar la conversión, configurar reintentos, ver progreso, revisar archivos
fallidos, abrir informes y ejecutar Doctor checks.

Para entornos restringidos, configura raíces permitidas:

```bash
export RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS="/input"
export RAWBRIDGE_UI_ALLOWED_OUTPUT_ROOTS="/output"
```

## Presets

| Preset | Salida | Uso típico |
| --- | --- | --- |
| `web` | WebP + JPEG, max 2560 px | Imágenes generales para sitios web |
| `preview` | WebP, max 1600 px, half-size decode | Previews rápidos |
| `retina` | WebP + JPEG responsive sizes | Pantallas de alta densidad |
| `lossless_web` | WebP sin pérdida + PNG | Exportaciones web de archivo |
| `tilda` | WebP + JPEG responsive sizes | Publicación en Tilda |
| `wordpress` | WebP + JPEG responsive sizes | Tamaños de medios de WordPress |

Puedes sobrescribir presets desde la CLI:

```bash
rawbridge convert ./RAW \
  --out ./web_export \
  --preset wordpress \
  --format webp,jpg \
  --responsive-sizes 768,1200,1536,2048 \
  --quality 86
```

## Reanudación, fallos y limpieza

Cada conversión escribe `.rawbridge_manifest.sqlite` en el directorio de salida.
Los outputs existentes se omiten por defecto cuando la reanudación está activa.

Las rutas fallidas se escriben en `rawbridge_failed.tsv`. Usa `--only-failed`
para reintentar solo esos archivos después de corregir credenciales, red o un
RAW problemático.

Comandos útiles:

```bash
rawbridge resume JOB_ID
rawbridge report JOB_ID
rawbridge clean --out ./web_export
```

## Informes

RawBridge escribe estos archivos en el directorio de salida:

- `report.json`
- `report.csv`
- `errors.csv`
- `assets.json`
- `report.html`
- `picture-snippets.html`
- `rawbridge_failed.tsv`

Los CSV están protegidos contra spreadsheet formula injection. Los snippets HTML
escapan rutas de archivos antes de escribirlas.

## Privacidad de metadatos

El modo predeterminado es `strip`. Elimina EXIF/GPS/metadatos privados de cámara
cuando el encoder lo permite. Usa `keep-color` si quieres conservar información
de perfil de color y aun así quitar metadatos privados. Usa `keep-all` solo en
flujos confiables que no sean públicos.

No publiques tokens de Dropbox, credenciales de Google, secretos de AWS, refresh
tokens OAuth, tokens de hosting Git ni secretos de CI en issues, logs, informes,
docs o scripts de espejos.

## Docker

Construye la imagen local:

```bash
docker build -t rawbridge:0.1.0 .
```

Ejecuta una conversión:

```bash
docker run --rm \
  -v "$PWD/RAW:/input:ro" \
  -v "$PWD/web_export:/output" \
  rawbridge:0.1.0 \
  rawbridge convert /input --provider local --out /output --preset web
```

Para proveedores cloud, pasa credenciales mediante variables de entorno en vez
de incluirlas en la imagen.

## Documentación

Empieza por:

- [Documentación en español](docs/es/index.md)
- [Inicio rápido](docs/es/quick-start.md)
- [Instalación](docs/es/installation.md)
- [Mirrors](MIRRORS.md)
- [Russian mirrors](RUSSIAN_MIRRORS.md)

## Desarrollo

Ejecuta tests:

```bash
pytest
```

Construye la documentación:

```bash
./scripts/build_docs.sh
```

Ejecuta un smoke test:

```bash
./scripts/smoke_test.sh
```

## Contribuir

Consulta [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md),
[SECURITY.md](SECURITY.md) y [ROADMAP.md](ROADMAP.md).

## Licencia

MIT. Consulta [LICENSE](LICENSE).
