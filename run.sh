#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python alarm_app/main.py
