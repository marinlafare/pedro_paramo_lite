#!/bin/sh

# Wait for the PostgreSQL database to be available
echo "Waiting for PostgreSQL to start..."
while ! pg_isready -h db -p 5432 -U postgres -d pedro_paramo_db > /dev/null; do
  sleep 1
done

echo "PostgreSQL is up and running. Starting the application..."

# Run your Python application
# Assuming your main API entry point is in a file like main.py
# If you are using FastAPI, this is a common way to run it.
# Replace this command with whatever command you use to start your application.
uvicorn main:app --host 0.0.0.0 --reload --port 9000