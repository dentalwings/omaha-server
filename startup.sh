#!/usr/bin/env bash
docker-compose up -d db redis
docker-compose build django

sleep 3

docker-compose up -d django
docker-compose exec -T django python manage.py migrate
docker-compose exec -T django python manage.py collectstatic
docker-compose exec -T django python createadmin.py
