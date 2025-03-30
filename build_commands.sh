#!/bin/sh

set -e

# Install OS dependencies
apt-get update && \
apt-get install -y cargo

# Install Python dependencies
pip install -r requirements.txt
