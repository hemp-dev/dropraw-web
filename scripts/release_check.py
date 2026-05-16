from __future__ import annotations

import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"


def main() -> int:
    failures: list[str] = []
    checks = [
        check_pyproject,
        check_required_files,
        check_docs,
        check_no_obvious_secrets,
        check_sync_scripts,
        check_build,
    ]
    for check in checks:
        try:
            failures.extend(check())
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{check.__name__} failed unexpectedly: {exc}")
    if failures:
        print("Release check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Release check passed.")
    return 0


def check_pyproject() -> list[str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data.get("project", {})
    failures = []
    if project.get("version") != VERSION:
        failures.append("pyproject version is not 0.1.0")
    if project.get("requires-python") != ">=3.11,<3.14":
        failures.append("pyproject requires-python must be >=3.11,<3.14")
    if not project.get("classifiers"):
        failures.append("pyproject classifiers are missing")
    if not project.get("keywords"):
        failures.append("pyproject keywords are missing")
    scripts = project.get("scripts", {})
    if scripts.get("rawbridge") != "rawbridge.cli:app":
        failures.append("rawbridge entry point is missing")
    return failures


def check_required_files() -> list[str]:
    required = [
        "README.md",
        "README.ru.md",
        "README.es.md",
        "README.zh.md",
        "README.de.md",
        "README.fr.md",
        "LICENSE",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "SUPPORT.md",
        "ROADMAP.md",
        "RELEASE_CHECKLIST.md",
        "MIRRORS.md",
        "RUSSIAN_MIRRORS.md",
        "CITATION.cff",
        ".env.example",
        "Dockerfile",
        "docker-compose.yml",
        ".github/workflows/tests.yml",
        ".github/workflows/release.yml",
        ".github/workflows/docker.yml",
        ".github/workflows/docs.yml",
        ".gitlab-ci.yml",
        "bitbucket-pipelines.yml",
        ".forgejo/workflows/tests.yml",
        "docs/release-notes/v0.1.0.md",
    ]
    return [f"missing required file: {path}" for path in required if not (ROOT / path).exists()]


def check_docs() -> list[str]:
    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [ROOT / "README.md", ROOT / "README.ru.md", ROOT / "docs/en/index.md", ROOT / "docs/ru/index.md"]
    )
    failures = []
    for needle in ["Python 3.11", "3.12", "retry", "failed", "resume", "816 Nikon NEF", "ConnectionError"]:
        if needle not in combined:
            failures.append(f"docs missing required mention: {needle}")
    return failures


def check_no_obvious_secrets() -> list[str]:
    failures = []
    secret_re = re.compile(r"(DROPBOX_ACCESS_TOKEN|AWS_SECRET_ACCESS_KEY|GITHUB_TOKEN|GL_TOKEN)[^\S\r\n]*=[^\S\r\n]*['\"]?[A-Za-z0-9_./+=-]{12,}")
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".venv", ".venv312", "node_modules", ".git", "dist", "build"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if secret_re.search(text):
            failures.append(f"possible secret in {path.relative_to(ROOT)}")
    return failures


def check_sync_scripts() -> list[str]:
    failures = []
    for name in ["sync_international_mirrors.sh", "sync_russian_mirrors.sh", "sync_all_mirrors.sh"]:
        text = (ROOT / "scripts" / name).read_text(encoding="utf-8")
        if "token" in text.lower() or "://" in text:
            failures.append(f"sync script should contain only remote names: {name}")
    return failures


def check_build() -> list[str]:
    if os.getenv("RAWBRIDGE_RELEASE_CHECK_BUILD") != "1":
        return []
    result = subprocess.run([sys.executable, "-m", "build"], cwd=ROOT, check=False)
    return [] if result.returncode == 0 else ["python -m build failed"]


if __name__ == "__main__":
    raise SystemExit(main())
