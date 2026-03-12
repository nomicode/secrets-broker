#!/bin/sh
set -e

# Trust the .envrc (adds ./node_modules/.bin to PATH)
direnv allow .

# Install node deps (trunk launcher + any future tooling)
yarn install

# Init trunk using direnv context so the just-installed binary is on PATH
direnv exec . trunk init
