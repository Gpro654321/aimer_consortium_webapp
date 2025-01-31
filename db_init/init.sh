#!/bin/bash
set -e

# Substitute environment variables into the SQL commands dynamically
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE "$POSTGRES_NAME";
    CREATE USER "$POSTGRES_USER" WITH PASSWORD '$POSTGRES_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_NAME" TO "$POSTGRES_USER";
EOSQL
