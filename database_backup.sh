#!/bin/bash

# Load environment variables from .env file
set -a
source ./.env
set +a

# Set variables from .env
DB_NAME="$POSTGRES_NAME"
DB_USER="$POSTGRES_USER"
BACKUP_DIR="./databackup"
BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql"

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Run `pg_dump` inside the `db` container
docker-compose exec -t db pg_dump -U "$DB_USER" -d "$DB_NAME" -F c -f "/var/lib/postgresql/data/db_backup.sql"

# Copy the backup file from the container to the host
docker-compose cp db:/var/lib/postgresql/data/db_backup.sql "$BACKUP_FILE"

# Delete old backups (older than 7 days)
find "$BACKUP_DIR" -type f -name "*.sql" -mtime +7 -exec rm {} \;

echo "✅ Backup completed: $BACKUP_FILE"
