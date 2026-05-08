#!/usr/bin/env bash

set -e
set -x

ruff check --diff src tests
ruff format --check --diff src tests
ty check src tests --output-format github

set +x
