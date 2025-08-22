#!/bin/bash
# Simple script to create testguru database if it doesn't exist

# Load secrets from secrets.yml
DB_USER=$(grep "db_user:" secrets.yml | awk '{print $2}' | tr -d '"')
DB_PASSWORD=$(grep "db_password:" secrets.yml | awk '{print $2}' | tr -d '"')

echo "Creating database testguru if it doesn't exist..."

# Check if database exists
PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d postgres -c "SELECT 1 FROM pg_database WHERE datname = 'testguru'" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Database testguru not found. Creating..."
    PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d postgres -c "CREATE DATABASE testguru"
    echo "Database testguru created successfully!"
else
    echo "Database testguru already exists."
fi

echo "Database setup complete!"
