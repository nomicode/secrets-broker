#!/bin/sh
# bootstrap.sh - set up the full dev environment from scratch.
# Safe to re-run. Installs missing tools automatically.
set -e

OS="$(uname -s)"
ARCH="$(uname -m)"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

has() { command -v "$1" > /dev/null 2>&1; }

need_brew() {
    if ! has brew; then
        printf 'error: Homebrew is required on macOS but not found.\n' >&2
        printf 'Install it from https://brew.sh then re-run.\n' >&2
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# direnv
# ---------------------------------------------------------------------------

if ! has direnv; then
    printf '=> installing direnv...\n'
    if test "${OS}" = "Darwin"; then
        need_brew
        brew install direnv
    elif test "${OS}" = "Linux"; then
        BIN_DIR="${HOME}/.local/bin"
        mkdir -p "${BIN_DIR}"
        case "${ARCH}" in
            x86_64)          DIRENV_ARCH="amd64" ;;
            aarch64|arm64)   DIRENV_ARCH="arm64" ;;
            *)
                printf 'error: unsupported arch %s\n' "${ARCH}" >&2
                exit 1
                ;;
        esac
        curl -fsSL \
            "https://github.com/direnv/direnv/releases/latest/download/direnv.linux-${DIRENV_ARCH}" \
            -o "${BIN_DIR}/direnv"
        chmod +x "${BIN_DIR}/direnv"
        export PATH="${BIN_DIR}:${PATH}"
        printf 'note: add %s to your PATH in your shell rc file.\n' "${BIN_DIR}"
    else
        printf 'error: unsupported OS %s\n' "${OS}" >&2
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# node + npm
# ---------------------------------------------------------------------------

if ! has node; then
    printf '=> installing node...\n'
    if test "${OS}" = "Darwin"; then
        need_brew
        brew install node
    elif test "${OS}" = "Linux"; then
        if has apt-get; then
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E sh -
            sudo apt-get install -y nodejs
        elif has yum; then
            curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo sh -
            sudo yum install -y nodejs
        else
            printf 'error: cannot auto-install node on this Linux distro.\n' >&2
            printf 'Install Node LTS manually: https://nodejs.org\n' >&2
            exit 1
        fi
    fi
fi

# ---------------------------------------------------------------------------
# yarn
# ---------------------------------------------------------------------------

if ! has yarn; then
    printf '=> installing yarn via npm...\n'
    npm install -g yarn
fi

# ---------------------------------------------------------------------------
# uv (Python package manager)
# ---------------------------------------------------------------------------

if ! has uv; then
    printf '=> installing uv...\n'
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${PATH}"
fi

# ---------------------------------------------------------------------------
# project bootstrap
# ---------------------------------------------------------------------------

printf '=> trusting .envrc...\n'
direnv allow .

printf '=> installing node deps (trunk, prettier)...\n'
yarn install

printf '=> installing python deps...\n'
uv sync --dev

printf '=> initialising trunk...\n'
direnv exec . trunk init

printf '\nDone. Run "direnv allow ." if prompted after shell reload.\n'
