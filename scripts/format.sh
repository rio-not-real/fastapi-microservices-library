#!/usr/bin/env bash

set -x

ruff check --fix src tests
ruff format src tests

set +x
