#!/usr/bin/env bash
set -euo pipefail
cd ..
mkdir -p flowshop_instances
cd flowshop_instances

curl --fail --location --remote-header-name --remote-name \
  'https://figshare.com/ndownloader/files/48152884'

echo "Descarga completada en: $(pwd)"
ls -lh
