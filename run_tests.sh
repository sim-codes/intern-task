#!/bin/bash
# Test runner script for the Django auth service

echo "Running Django tests for users app..."

# Set Django settings module
export DJANGO_SETTINGS_MODULE=auth_service.settings

# Run tests
python manage.py test users --verbosity=2
