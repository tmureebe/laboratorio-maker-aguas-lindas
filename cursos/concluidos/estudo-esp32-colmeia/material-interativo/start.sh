#!/usr/bin/env bash
set -eu
COURSE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec python3 "$COURSE_ROOT/serve.py" --directory "$COURSE_ROOT" "$@"
