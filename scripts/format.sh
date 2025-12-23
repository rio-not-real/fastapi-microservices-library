#!/usr/bin/env bash

ruff check --fix src tests scripts
ruff format src tests scripts
