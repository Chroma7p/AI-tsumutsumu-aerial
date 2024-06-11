# Pythonの公式イメージをベースにする
FROM python:3.11-bookworm

# 作業ディレクトリを設定
WORKDIR /bot

# Poetryをインストール
RUN pip install poetry

# プロジェクトの依存ファイルをコピー
COPY pyproject.toml poetry.lock tox.ini README.md schema.prisma ./

# Poetryの設定を行い、依存関係をインストール
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Botのソースコードをコピー
COPY src/ ./src/

RUN poetry install
