#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p var/sessions
chmod 700 var/sessions
if command -v php >/dev/null 2>&1; then
  exec php -d session.save_path="$PWD/var/sessions" -S 127.0.0.1:8080 -t public
fi
export LD_LIBRARY_PATH="/workspace/tooling/php/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec /workspace/tooling/php/usr/bin/php8.4 -d session.save_path="$PWD/var/sessions" -S 127.0.0.1:8080 -t public
