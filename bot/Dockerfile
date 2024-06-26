# Pythonの公式イメージをベースにする
FROM python:3.11-bookworm

RUN apt-get update && apt-get -y install netcat-traditional

COPY bot/schema.prisma ./bot/schema.prisma

# 作業ディレクトリを設定
WORKDIR /bot

# Poetryをインストール
RUN pip install poetry

# プロジェクトの依存ファイルをコピー
COPY bot/pyproject.toml bot/poetry.lock bot/tox.ini bot/README.md bot/wait-for-pg.sh ./
RUN chmod +x ./wait-for-pg.sh

# Poetryの設定を行い、依存関係をインストール
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi

# Botのソースコードをコピー
COPY bot/src/ ./src/

ARG GENERATOR_PROVIDER
ARG POSTGRES_URL

ENTRYPOINT [ "sh","-c","./wait-for-pg.sh" ]

