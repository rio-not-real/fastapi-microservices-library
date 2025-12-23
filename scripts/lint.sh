#!/usr/bin/env bash

ruff check --diff src tests scripts
ruff format --check --diff src tests scripts
ty check src tests scripts --output-format github
