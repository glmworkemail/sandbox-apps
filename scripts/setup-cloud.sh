#!/bin/sh
# Non-root cloud PHP runtime. Debian APT verifies repository signatures and packages.
set -eu
if command -v php >/dev/null 2>&1; then
  php -r 'exit(PHP_VERSION_ID >= 80200 && extension_loaded("openssl") && extension_loaded("session") ? 0 : 1);'
  exit 0
fi
base=/workspace/tooling
if [ -x "$base/php/usr/bin/php8.4" ]; then
  LD_LIBRARY_PATH="$base/php/usr/lib/x86_64-linux-gnu" "$base/php/usr/bin/php8.4" -r 'exit(PHP_VERSION_ID >= 80200 && extension_loaded("openssl") && extension_loaded("session") ? 0 : 1);'
  exit 0
fi
mkdir -p "$base/apt/lists/partial" "$base/apt/cache/archives/partial" "$base/apt/config" "$base/apt/sources"
printf '%s\n' 'deb https://deb.debian.org/debian trixie main' > "$base/apt/sources.list"
cd "$base"
apt_local() {
  /usr/bin/apt-get -o Dir::State::lists="$base/apt/lists" -o Dir::Cache="$base/apt/cache" -o Dir::Etc::parts="$base/apt/config" -o Dir::Etc::sourcelist="$base/apt/sources.list" -o Dir::Etc::sourceparts="$base/apt/sources" -o APT::Sandbox::User="$(id -un)" "$@"
}
apt_local update
apt_local download php8.4-cli php8.4-common libxml2 libpcre2-8-0 libsodium23 libargon2-1 libedit2
for package in ./*.deb; do dpkg-deb -x "$package" "$base/php"; done
LD_LIBRARY_PATH="$base/php/usr/lib/x86_64-linux-gnu" "$base/php/usr/bin/php8.4" -r 'exit(PHP_VERSION_ID >= 80200 && extension_loaded("openssl") && extension_loaded("session") ? 0 : 1);'
