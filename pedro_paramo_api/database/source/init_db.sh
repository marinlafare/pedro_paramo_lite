#!/bin/bash
set -e

# This script runs inside the PostgreSQL container during its initial setup.
# It restores the database from a pg_dump file.

echo "PostgreSQL is ready. Restoring database from dump file..."

# Restore the database from the .dump file using pg_restore.
# The -d flag specifies the database to restore into.
# The -v flag provides verbose output.
# The dump file is located at /docker-entrypoint-initdb.d/dissection_table_backup.dump
pg_restore -v -d "$POSTGRES_DB" "/docker-entrypoint-initdb.d/dissection_table_backup.dump" \
  --username="$POSTGRES_USER" \
  --no-owner \
  --clean \
  --if-exists

echo "Database restore complete from dissection_table_backup.dump."
