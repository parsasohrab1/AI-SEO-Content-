#!/bin/bash

# Monitoring Script - بررسی سلامت سرویس‌ها

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Service Health Check ===${NC}\n"

# Check API
echo -n "API Health: "
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Check Frontend
echo -n "Frontend Health: "
if curl -f -s http://localhost:3002 > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Check Database
echo -n "PostgreSQL: "
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Check MongoDB
echo -n "MongoDB: "
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Check Redis
echo -n "Redis: "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Check RabbitMQ
echo -n "RabbitMQ: "
if docker-compose exec -T rabbitmq rabbitmq-diagnostics ping > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Check Disk Space
echo -e "\n${YELLOW}=== Disk Usage ===${NC}"
df -h | grep -E '^/dev/'

# Check Memory
echo -e "\n${YELLOW}=== Memory Usage ===${NC}"
free -h

# Check Docker Containers
echo -e "\n${YELLOW}=== Container Status ===${NC}"
docker-compose ps

echo -e "\n${GREEN}Health check completed${NC}"

