#!/bin/bash

# Backup Script for AI Content Factory Pro
# این اسکریپت Backup کامل از تمام Databaseها و Dataها می‌گیرد

set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting backup process...${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

# Backup PostgreSQL
echo -e "${YELLOW}Backing up PostgreSQL...${NC}"
docker-compose exec -T db pg_dump -U postgres content_factory > "$BACKUP_DIR/$TIMESTAMP/postgres_backup.sql"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}PostgreSQL backup completed${NC}"
else
    echo -e "${RED}PostgreSQL backup failed${NC}"
    exit 1
fi

# Backup MongoDB
echo -e "${YELLOW}Backing up MongoDB...${NC}"
docker-compose exec -T mongodb mongodump --archive > "$BACKUP_DIR/$TIMESTAMP/mongodb_backup.archive"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}MongoDB backup completed${NC}"
else
    echo -e "${RED}MongoDB backup failed${NC}"
    exit 1
fi

# Backup Redis (if needed)
echo -e "${YELLOW}Backing up Redis...${NC}"
docker-compose exec -T redis redis-cli --rdb "$BACKUP_DIR/$TIMESTAMP/redis_backup.rdb" || true

# Backup application data
echo -e "${YELLOW}Backing up application data...${NC}"
if [ -d "./data" ]; then
    tar -czf "$BACKUP_DIR/$TIMESTAMP/data_backup.tar.gz" ./data
    echo -e "${GREEN}Application data backup completed${NC}"
fi

# Create backup info file
cat > "$BACKUP_DIR/$TIMESTAMP/backup_info.txt" << EOF
Backup Date: $(date)
Backup Type: Full
PostgreSQL: Yes
MongoDB: Yes
Redis: Yes
Application Data: Yes
EOF

# Compress backup
echo -e "${YELLOW}Compressing backup...${NC}"
cd "$BACKUP_DIR"
tar -czf "backup_$TIMESTAMP.tar.gz" "$TIMESTAMP"
rm -rf "$TIMESTAMP"
cd ..

echo -e "${GREEN}Backup completed: backup_$TIMESTAMP.tar.gz${NC}"

# Cleanup old backups
echo -e "${YELLOW}Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo -e "${GREEN}Cleanup completed${NC}"

echo -e "${GREEN}Backup process finished successfully!${NC}"

