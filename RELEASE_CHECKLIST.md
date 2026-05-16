# Release Checklist

## Before Tagging

- [ ] Tests pass.
- [ ] UI builds.
- [ ] Docker builds.
- [ ] README updated.
- [ ] Localized READMEs updated.
- [ ] CHANGELOG updated.
- [ ] Version updated.
- [ ] Docs updated.
- [ ] MIRRORS.md updated.
- [ ] RUSSIAN_MIRRORS.md updated.
- [ ] No secrets committed.
- [ ] `.env.example` updated.
- [ ] Release notes ready.
- [ ] PyPI package builds.
- [ ] Docker image builds.
- [ ] GitHub Release draft ready.
- [ ] GitLab mirror ready.
- [ ] Bitbucket mirror ready.
- [ ] Codeberg mirror ready.
- [ ] GitFlic mirror ready if used.
- [ ] GitVerse mirror ready if used.

## Release

- [ ] `git tag v0.1.0`.
- [ ] `git push origin v0.1.0`.
- [ ] GitHub Actions release passed.
- [ ] PyPI published.
- [ ] Docker image published.
- [ ] Docs deployed.
- [ ] International mirrors synced.
- [ ] Russian mirrors synced if configured.

## After Release

- [ ] Test `pip install rawbridge` from PyPI.
- [ ] Test Docker pull.
- [ ] Check GitHub release assets.
- [ ] Check GitLab mirror.
- [ ] Check Codeberg mirror.
- [ ] Check Bitbucket mirror.
- [ ] Check GitFlic mirror if configured.
- [ ] Check GitVerse mirror if configured.
- [ ] Check docs site.
- [ ] Announce launch.
