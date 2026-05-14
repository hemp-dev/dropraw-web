#!/usr/bin/env bash
set -euo pipefail

./scripts/sync_international_mirrors.sh
./scripts/sync_russian_mirrors.sh
