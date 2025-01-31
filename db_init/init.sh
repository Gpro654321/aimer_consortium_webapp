#!/bin/bash
set -e

# Attempt to create the database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE DATABASE "$POSTGRES_NAME"' 
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_NAME')\gexec
EOSQL

# Attempt to create the user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE USER "$POSTGRES_USER" WITH PASSWORD ''$POSTGRES_PASSWORD''' 
    WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$POSTGRES_USER')\gexec
EOSQL

# Grant privileges to the user on the database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_NAME" TO "$POSTGRES_USER";
EOSQL
