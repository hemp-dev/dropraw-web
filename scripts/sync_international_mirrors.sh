#!/usr/bin/env bash
set -euo pipefail

git push github main --tags
git push gitlab main --tags
git push bitbucket main --tags
git push codeberg main --tags
