# Contributing

Thanks for helping make RawBridge better.

## Development Setup

Use Python 3.11 or 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
rawbridge doctor
rawbridge --version
```

## Running UI

```bash
cd ui
npm ci
npm run build
cd ..
rawbridge ui
```

## Adding A Provider

- Implement the `StorageProvider` interface.
- Support `list_files`.
- Support `download_file`.
- Support stable `fingerprint` values.
- Add tests.
- Add docs.
- Never download whole folder archives for large sources if API listing is possible.
- Support retry and `.part` download behavior where possible.

## Adding An Output Encoder

- Keep encoder logic isolated under `src/rawbridge/imaging`.
- Add format validation.
- Add tests for extension, MIME expectations, and metadata behavior.
- Document optional system/package dependencies.

## Adding Mirror Docs

- Add the platform to `MIRRORS.md`.
- Explain whether it is primary, mirror, self-hosted, enterprise, optional, or experimental.
- Add a remote template only if the URL format is known.
- Do not add secrets.
- Do not claim an active mirror unless it is verified.

## Documentation Changes

- Do not translate command names, CLI flags, file names, or platform names.
- Keep examples copy-paste friendly.
- Be honest about credentials, provider limitations, and optional mirrors.
- Update localized docs when changing core usage.

## Code Style

- Keep core pipeline changes small and tested.
- Prefer existing abstractions and provider boundaries.
- Do not duplicate conversion pipeline logic in UI code.
- Preserve Dropbox shared-link download path behavior.

## Security Rules

- Do not log access tokens, shared-link passwords, OAuth refresh tokens, AWS secrets, Git hosting tokens, or CI secrets.
- Do not commit `.env`, service account JSON, private keys, or downloaded RAW archives.
- Use mocks for cloud-provider tests unless explicit integration credentials are configured outside the repository.

## Pull Request Checklist

- Tests pass.
- Docs are updated.
- Release notes or changelog are updated when user-facing behavior changes.
- Security/privacy impact is described.
- Provider changes include retry/resume considerations.
