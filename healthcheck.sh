#!/bin/bash

# Check if the PostgreSQL server is ready
pg_isready -q -d $POSTGRES_NAME -U $POSTGRES_USER

if [ $? -eq 0 ]; then
  # If PostgreSQL is ready, create an empty file named "test" in the home directory
  touch ./test_xyz123
  exit 0
else
  exit 1
fi
