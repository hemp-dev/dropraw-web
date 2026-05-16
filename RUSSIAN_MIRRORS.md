# Российские Git / DevOps площадки для RawBridge

## Зачем Нужны Российские Зеркала

Российские зеркала помогают обеспечить доступность для российских команд, импортозамещение, работу в корпоративных DevOps-контурах, публикацию на локальных open-source площадках, а также более понятный supply-chain для доверенных зависимостей.

## GitFlic

GitFlic рассматривается как основной российский public mirror для RawBridge. Он подходит для open-source и private repositories.

```bash
git remote add gitflic git@gitflic.ru:hemp-dev/rawbridge.git
```

Не помечайте GitFlic mirror как active, пока repository, push, tags и release workflow не проверены.

## GitVerse

GitVerse рассматривается как второй российский public/private mirror. Он подходит для командной разработки и open-source публикации.

```bash
git remote add gitverse git@gitverse.ru:hemp-dev/rawbridge.git
```

Не помечайте GitVerse mirror как active, пока repository, push, tags и release workflow не проверены.

## Сфера.Код / Платформа Сфера

Сфера.Код / Платформа Сфера рассматривается как enterprise/self-hosted DevOps target. Это не обязательно public mirror.

Нейтральный workflow:

```bash
git remote add sfera git@sfera.example.ru:TEAM/rawbridge.git
git push sfera main --tags
```

Создайте внутренний репозиторий в вашей инсталляции Сфера.Код и добавьте его как remote. CI, registry, approvals и release gates зависят от конкретной корпоративной инсталляции.

## РТК-Феникс

РТК-Феникс рассматривается как secure supply-chain / dependency repository context. Не описывайте его как прямой GitHub replacement без подтвержденного Git-hosting workflow.

Используйте этот контекст для проверки open-source компонентов, доверенных зависимостей, внутреннего dependency governance и supply-chain документации, если он доступен в вашей организации.

## Mos.Hub

Mos.Hub является optional public-sector/open-source target. Используйте его только если регистрация, repository creation и mirror workflow доступны и проверены.

Placeholder template:

```bash
git remote add moshub git@moshub.example:hemp-dev/rawbridge.git
```

Этот remote template не является подтверждением active mirror.

## Национальный Репозиторий Открытого Кода / РФРИТ

Национальный репозиторий открытого кода / РФРИТ рассматривается как strategic/government context. Не делайте его required release target без стабильного публичного процесса и проверенного workflow.

## Recommended Russian Strategy

- Main Russian mirror: GitFlic.
- Secondary Russian mirror: GitVerse.
- Enterprise documentation: Сфера.Код.
- Security/supply-chain note: РТК-Феникс.
- Optional: Mos.Hub / National repository.

## Sync Commands

```bash
./scripts/sync_russian_mirrors.sh
```

The script expects placeholder remote names to be configured manually.

## Important Warnings

- Не публиковать токены.
- Не коммитить `.env`.
- Не заявлять mirror как active, пока он не проверен.
- Не обещать поддержку platforms, которые experimental.
- Не добавлять registry claims без проверки.
- Не хранить credentials в mirror scripts.
