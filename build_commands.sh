#!/bin/sh

set -e

# Install OS dependencies
apt-get update && \
apt-get install cargo

# Install Python dependencies
pip install -r requirements.txt
