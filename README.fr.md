# RawBridge

[English](README.md) | [Русский](README.ru.md) |
[Español](README.es.md) | [中文](README.zh.md) |
[Deutsch](README.de.md) | Français

RawBridge convertit de grands dossiers de photos RAW depuis Dropbox,
Google Drive, des stockages compatibles S3 et des disques locaux en images
prêtes pour le web.

Il évite le flux fragile qui consiste à télécharger tout un dossier sous forme
d'une énorme archive ZIP. RawBridge liste la source, télécharge les fichiers RAW
un par un, les convertit, enregistre la progression dans un manifeste local et
permet de reprendre après une erreur réseau ou de traitement.

## État du projet

RawBridge est une version open-source initiale. Le paquet Python s'appelle
`rawbridge` et la commande CLI principale est `rawbridge`.

Les versions recommandées de Python sont 3.11 et 3.12. Python 3.14 n'est pas
dans la plage prise en charge pour cette ligne de version, car certaines
dépendances d'imagerie et de SDK cloud peuvent prendre du retard.

## À quoi sert RawBridge

Utilisez RawBridge si vous devez :

- convertir un dossier Dropbox partagé de fichiers RAW en WebP/JPEG sans échec
  d'export ZIP ;
- préparer une archive RAW locale pour un site, un CMS, un catalogue, une
  galerie ou une livraison design ;
- convertir des dossiers Google Drive, S3, R2 ou MinIO vers une structure de
  sortie prévisible ;
- relancer uniquement les fichiers en échec après une longue tâche cloud ;
- générer des rapports et des extraits `<picture>` pour la publication web ;
- supprimer les données GPS et les métadonnées privées de caméra avant la mise
  en ligne.

## Fonctionnalités

- CLI et interface web locale.
- Prise en charge des dossiers locaux et des liens partagés Dropbox.
- Prise en charge expérimentale de Google Drive et S3/R2/MinIO.
- Sorties WebP, AVIF, JPEG et PNG.
- Presets pour web, previews, retina, Tilda, WordPress et exports web sans
  perte.
- Variantes responsive comme `image@1200.webp`.
- Manifeste SQLite de reprise dans le dossier de sortie.
- Journal des fichiers en échec et relance avec `--only-failed`.
- Reprises de listing et de téléchargement, exponential backoff, cooldowns,
  téléchargements `.part` et vérifications de taille.
- Rapports JSON, CSV, HTML, assets, erreurs et picture snippets.
- Modes de confidentialité des métadonnées : `strip`, `keep-color` et
  `keep-all`.
- Support Docker et docker-compose.

## Sources prises en charge

| Provider | État | Exemple de source |
| --- | --- | --- |
| `local` | Stable | `./RAW` |
| `dropbox` | Stable | `https://www.dropbox.com/scl/fo/...` |
| `google-drive` | Expérimental | `https://drive.google.com/drive/folders/FOLDER_ID` |
| `s3` | Expérimental | `s3://bucket/raw` |
| `r2` | Expérimental via le provider S3 | `r2://bucket/raw` |
| `minio` | Expérimental via le provider S3 | `minio://bucket/raw` |
| `onedrive` | À venir | Squelette de provider uniquement |
| `yadisk` | À venir | Squelette de provider uniquement |
| `box` | À venir | Squelette de provider uniquement |

Les extensions RAW prises en charge incluent `NEF`, `NRW`, `CR2`, `CR3`,
`ARW`, `RAF`, `RW2`, `ORF`, `DNG`, `PEF`, `RAW`, `RWL`, `IIQ`, `3FR`, `ERF`,
`MEF`, `MOS`, `MRW`, `SRW` et `X3F`.

La sortie AVIF dépend du support AVIF dans la version installée de Pillow.
Exécutez `rawbridge doctor` pour vérifier l'environnement.

## Installation

Pour le développement local ou l'exécution depuis ce dépôt :

```bash
git clone https://github.com/hemp-dev/rawbridge.git
cd rawbridge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Lorsque le paquet est disponible dans votre package index, installez-le avec :

```bash
pip install rawbridge
```

## Démarrage rapide

```bash
rawbridge --version
rawbridge doctor
rawbridge scan ./RAW
rawbridge convert ./RAW --out ./web_export --preset web
```

Le preset `web` écrit des fichiers WebP et JPEG, limite le plus grand côté à
2560 px, utilise quality `88` et supprime les métadonnées.

## Dropbox

Définissez un token Dropbox dans votre shell ou dans un fichier local `.env` :

```bash
export DROPBOX_ACCESS_TOKEN="..."
```

Convertissez un dossier partagé :

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

RawBridge a été testé sur un vrai dossier Dropbox partagé contenant 816 fichiers
Nikon NEF. Les erreurs transitoires Dropbox, SSL et réseau sont retentées. Si un
fichier réussit après retry, il est compté comme traité, pas comme échoué.

Relancez uniquement les fichiers en échec :

```bash
rawbridge convert "https://www.dropbox.com/scl/fo/..." \
  --provider dropbox \
  --out ./web_export \
  --only-failed ./web_export/rawbridge_failed.tsv
```

## Google Drive

Google Drive nécessite un fichier de service account ou une API key :

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
# ou
export GOOGLE_API_KEY="..."
```

Puis lancez :

```bash
rawbridge convert "https://drive.google.com/drive/folders/FOLDER_ID" \
  --provider google-drive \
  --out ./web_export \
  --preset web
```

Avec un service account, partagez le dossier Drive avec l'adresse email de ce
service account.

## S3, Cloudflare R2 et MinIO

AWS S3 utilise les variables d'environnement AWS standard :

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"

rawbridge convert s3://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Cloudflare R2 et MinIO nécessitent un endpoint compatible S3 :

```bash
export AWS_ENDPOINT_URL="https://ACCOUNT_ID.r2.cloudflarestorage.com"

rawbridge convert r2://bucket/raw \
  --provider s3 \
  --out ./web_export \
  --preset web
```

Vous pouvez aussi utiliser `S3_ENDPOINT_URL` au lieu de `AWS_ENDPOINT_URL`.

## Interface web locale

Démarrez l'interface locale :

```bash
rawbridge ui
```

Ouvrez `http://127.0.0.1:8787`. L'interface permet de configurer la source,
scanner, régler la conversion, configurer les retries, suivre la progression,
voir les fichiers en échec, ouvrir les rapports et lancer les Doctor checks.

Pour les environnements restreints, configurez les racines autorisées :

```bash
export RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS="/input"
export RAWBRIDGE_UI_ALLOWED_OUTPUT_ROOTS="/output"
```

## Presets

| Preset | Sortie | Usage typique |
| --- | --- | --- |
| `web` | WebP + JPEG, max 2560 px | Images générales de site web |
| `preview` | WebP, max 1600 px, half-size decode | Aperçus rapides |
| `retina` | WebP + JPEG responsive sizes | Écrans haute densité |
| `lossless_web` | WebP sans perte + PNG | Exports web d'archive |
| `tilda` | WebP + JPEG responsive sizes | Publication Tilda |
| `wordpress` | WebP + JPEG responsive sizes | Tailles média WordPress |

Vous pouvez remplacer les valeurs du preset depuis la CLI :

```bash
rawbridge convert ./RAW \
  --out ./web_export \
  --preset wordpress \
  --format webp,jpg \
  --responsive-sizes 768,1200,1536,2048 \
  --quality 86
```

## Reprise, fichiers en échec et nettoyage

Chaque conversion écrit `.rawbridge_manifest.sqlite` dans le dossier de sortie.
Les fichiers de sortie existants sont ignorés par défaut lorsque la reprise est
active.

Les chemins en échec sont écrits dans `rawbridge_failed.tsv`. Utilisez
`--only-failed` pour relancer uniquement ces fichiers après correction des
identifiants, de l'accès réseau ou d'un fichier RAW problématique.

Commandes utiles :

```bash
rawbridge resume JOB_ID
rawbridge report JOB_ID
rawbridge clean --out ./web_export
```

## Rapports

RawBridge écrit ces fichiers dans le dossier de sortie :

- `report.json`
- `report.csv`
- `errors.csv`
- `assets.json`
- `report.html`
- `picture-snippets.html`
- `rawbridge_failed.tsv`

Les rapports CSV sont protégés contre la spreadsheet formula injection. Les
snippets HTML échappent les chemins de fichiers avant l'écriture.

## Confidentialité des métadonnées

Le mode par défaut est `strip`. Il supprime les données EXIF/GPS et les
métadonnées privées de caméra lorsque l'encoder le permet. Utilisez
`keep-color` pour conserver les profils couleur tout en retirant les métadonnées
privées. Utilisez `keep-all` seulement dans des workflows fiables et non
publics.

Ne publiez jamais de tokens Dropbox, identifiants Google, secrets AWS, refresh
tokens OAuth, tokens d'hébergement Git ou secrets CI dans les issues, logs,
rapports, docs ou scripts de miroir.

## Docker

Construisez l'image locale :

```bash
docker build -t rawbridge:0.1.0 .
```

Lancez une conversion :

```bash
docker run --rm \
  -v "$PWD/RAW:/input:ro" \
  -v "$PWD/web_export:/output" \
  rawbridge:0.1.0 \
  rawbridge convert /input --provider local --out /output --preset web
```

Pour les providers cloud, transmettez les identifiants avec des variables
d'environnement plutôt que de les intégrer dans l'image.

## Documentation

Commencez par :

- [Documentation en français](docs/fr/index.md)
- [Démarrage rapide](docs/fr/quick-start.md)
- [Installation](docs/fr/installation.md)
- [Mirrors](MIRRORS.md)
- [Russian mirrors](RUSSIAN_MIRRORS.md)

## Développement

Lancez les tests :

```bash
pytest
```

Construisez la documentation :

```bash
./scripts/build_docs.sh
```

Lancez un smoke test :

```bash
./scripts/smoke_test.sh
```

## Contribuer

Consultez [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md),
[SECURITY.md](SECURITY.md) et [ROADMAP.md](ROADMAP.md).

## Licence

MIT. Consultez [LICENSE](LICENSE).
