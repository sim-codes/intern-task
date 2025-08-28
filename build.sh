#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify the following line to set the desired environment
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

python manage.py migrate
