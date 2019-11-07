#!/bin/bash
echo Installing 3deposit...
docker network create proxy
docker-compose -f init.yml up --build -d --force-recreate
docker-compose -f docker-compose.yml up --build -d

