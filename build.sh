#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
cd taskscheduler
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Seed the database with initial data
python manage.py seed_db

# Seed the database with initial data (only if tables are empty)
python manage.py seed_db || echo "Seeding failed or already seeded"