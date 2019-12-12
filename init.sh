#!/bin/bash
echo -e '\033[1;32mInstalling 3deposit...\033[0m'
docker network create proxy
docker-compose -f init.yml up --build -d --force-recreate
docker-compose -f docker-compose.yml up --build -d
echo -e '\033[1;32m3deposit installed!\033[0m'

