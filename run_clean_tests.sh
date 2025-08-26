#!/bin/bash
export PYTHONWARNINGS="ignore"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
pytest "$@"
