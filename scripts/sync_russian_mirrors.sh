#!/usr/bin/env bash
set -euo pipefail

git push gitflic main --tags
git push gitverse main --tags

# Optional enterprise/public-sector remotes, only after verification:
# git push sfera main --tags
# git push moshub main --tags
