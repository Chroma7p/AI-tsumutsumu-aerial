#!/bin/bash

# .envファイルを読み込む
set -a
source ../.env.local
set +a

echo "DATABASE_URL=$DATABASE_URL"
prisma db push