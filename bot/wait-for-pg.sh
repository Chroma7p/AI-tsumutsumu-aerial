#!/bin/sh
# Postgresが立ち上がるのを待つ
echo "Waiting for postgres-db..."
while ! nc -z postgres-db 5432; do
  sleep 1
done
echo "Postgres is up - executing command"

# PrismaデータベースのプッシュとBotの起動
poetry run prisma db push
poetry run python -u src/seed.py
echo "Bot is up - executing command"
poetry run python -u src/bot.py 
