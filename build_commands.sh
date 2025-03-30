#!/bin/sh

set -e

# Install OS dependencies
apt-get update && \
apt-get install -y curl build-essential

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh && \
. "$HOME/.local/bin/env" && \
uv sync

# Install Python dependencies
# pip install -r requirements.txt
