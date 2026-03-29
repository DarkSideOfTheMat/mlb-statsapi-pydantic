#!/bin/bash

source .venv/bin/activate && python3 -m pytest tests/ -x -q >&2
if [ $? -eq 1 ]; then
  exit 2 # Exit code 2 tells Claude to treat as feedback/error
else
  exit 0 # Exit code 0 means success, continue
fi
