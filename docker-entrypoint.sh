#!/bin/sh

uv run app database upgrade --no-prompt head
exec "$@"