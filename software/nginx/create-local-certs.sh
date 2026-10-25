#!/usr/bin/env bash
# Private loopback TLS only; never replace the public VPS Certbot certificates.
set -euo pipefail
umask 077
cert_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/certs"
command -v openssl >/dev/null || { echo 'OpenSSL is required.' >&2; exit 1; }
[[ ! -L "$cert_dir" ]] || { echo 'Refusing a symlinked certs directory.' >&2; exit 1; }
mkdir -p -- "$cert_dir"
mkdir -- "$cert_dir/.create-lock" || { echo 'Certificate creation is already locked.' >&2; exit 1; }
trap 'rmdir -- "$cert_dir/.create-lock"' EXIT
for name in localhost.pem localhost-key.pem; do
    if [[ -e "$cert_dir/$name" || -L "$cert_dir/$name" ]]; then
        echo 'Existing certificate files must not be overwritten.' >&2
        exit 1
    fi
done
(
    cd -- "$cert_dir"
    MSYS_NO_PATHCONV=1 openssl req -x509 -newkey rsa:2048 -nodes -sha256 -days 365 \
        -subj '/CN=localhost' -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1' \
        -addext 'basicConstraints=critical,CA:FALSE' \
        -keyout localhost-key.pem -out localhost.pem
)
chmod 600 "$cert_dir/localhost-key.pem"
echo 'Private certificates created. They are not automatically browser-trusted.'
