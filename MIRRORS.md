# Mirrors

## Primary Repository

Primary repository: GitHub.

Template:

```bash
git remote add github git@github.com:hemp-dev/rawbridge.git
```

GitHub is primary unless maintainers explicitly change this.

## International Mirrors

Recommended international mirrors:

- GitLab.
- Codeberg.
- Bitbucket.

Templates:

```bash
git remote add gitlab git@gitlab.com:hemp-dev/rawbridge.git
git remote add bitbucket git@bitbucket.org:hemp-dev/rawbridge.git
git remote add codeberg git@codeberg.org:hemp-dev/rawbridge.git
```

Do not claim an active mirror until the remote exists, sync succeeds, and release assets/docs are checked.

## Russian Mirrors

Recommended Russian public mirrors:

- GitFlic as the main Russian public mirror.
- GitVerse as the secondary Russian public/private mirror.

Templates:

```bash
git remote add gitflic git@gitflic.ru:hemp-dev/rawbridge.git
git remote add gitverse git@gitverse.ru:hemp-dev/rawbridge.git
```

See [RUSSIAN_MIRRORS.md](RUSSIAN_MIRRORS.md).

## Self-hosted Mirrors

Forgejo and Gitea are recommended for self-hosted deployments.

```bash
git remote add forgejo git@git.example.com:TEAM/rawbridge.git
git remote add gitea git@gitea.example.com:TEAM/rawbridge.git
```

Сфера.Код / Платформа Сфера is treated as a Russian enterprise/self-hosted DevOps target, not necessarily a public mirror.

```bash
git remote add sfera git@sfera.example.ru:TEAM/rawbridge.git
```

Do not assume every Forgejo/Gitea/Сфера.Код instance has CI enabled.

## Optional Mirrors

Optional or advanced targets:

- SourceHut.
- Radicle.
- Launchpad.
- AWS CodeCommit for enterprise environments.
- Mos.Hub when registration and mirror workflow are verified.

Use these only when maintainers have access and a clear sync process.

## Archive / Preservation

Software Heritage may be used for long-term preservation after the public repository exists.

## Sync Scripts

Before running sync scripts, manually add and verify remotes:

```bash
git remote add github git@github.com:hemp-dev/rawbridge.git
git remote add gitlab git@gitlab.com:hemp-dev/rawbridge.git
git remote add bitbucket git@bitbucket.org:hemp-dev/rawbridge.git
git remote add codeberg git@codeberg.org:hemp-dev/rawbridge.git
git remote add gitflic git@gitflic.ru:hemp-dev/rawbridge.git
git remote add gitverse git@gitverse.ru:hemp-dev/rawbridge.git
```

Then run:

```bash
./scripts/sync_international_mirrors.sh
./scripts/sync_russian_mirrors.sh
./scripts/sync_all_mirrors.sh
```

## Rules For Mirrors

- GitHub is primary unless maintainers change this.
- GitLab, Codeberg, and Bitbucket are international mirrors.
- GitFlic and GitVerse are Russian mirrors.
- Сфера.Код is a Russian enterprise/self-hosted DevOps target.
- РТК-Феникс is a secure dependency / supply-chain context, not necessarily a Git mirror.
- Mos.Hub is optional until workflow is verified.
- National repository / РФРИТ is strategic context unless a stable public workflow exists.
- Do not claim active mirrors unless remotes are configured and verified.
- Do not include real tokens or credentials in mirror scripts.
- Do not treat all mirrors equally.
