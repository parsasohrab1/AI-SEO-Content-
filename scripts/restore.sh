#!/bin/bash

# Restore Script for AI Content Factory Pro
# این اسکریپت Backup را Restore می‌کند

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <backup_file.tar.gz>${NC}"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}WARNING: This will restore the backup and may overwrite existing data!${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

echo -e "${GREEN}Starting restore process...${NC}"

# Extract backup
TEMP_DIR=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
BACKUP_DIR=$(find "$TEMP_DIR" -type d -mindepth 1 -maxdepth 1 | head -1)

# Restore PostgreSQL
if [ -f "$BACKUP_DIR/postgres_backup.sql" ]; then
    echo -e "${YELLOW}Restoring PostgreSQL...${NC}"
    docker-compose exec -T db psql -U postgres -d content_factory < "$BACKUP_DIR/postgres_backup.sql"
    echo -e "${GREEN}PostgreSQL restored${NC}"
fi

# Restore MongoDB
if [ -f "$BACKUP_DIR/mongodb_backup.archive" ]; then
    echo -e "${YELLOW}Restoring MongoDB...${NC}"
    docker-compose exec -T mongodb mongorestore --archive < "$BACKUP_DIR/mongodb_backup.archive"
    echo -e "${GREEN}MongoDB restored${NC}"
fi

# Restore Redis
if [ -f "$BACKUP_DIR/redis_backup.rdb" ]; then
    echo -e "${YELLOW}Restoring Redis...${NC}"
    docker-compose cp "$BACKUP_DIR/redis_backup.rdb" redis:/data/dump.rdb
    docker-compose restart redis
    echo -e "${GREEN}Redis restored${NC}"
fi

# Restore application data
if [ -f "$BACKUP_DIR/data_backup.tar.gz" ]; then
    echo -e "${YELLOW}Restoring application data...${NC}"
    tar -xzf "$BACKUP_DIR/data_backup.tar.gz" -C ./
    echo -e "${GREEN}Application data restored${NC}"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}Restore completed successfully!${NC}"

