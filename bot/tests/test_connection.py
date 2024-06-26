import psycopg2
import qdrant_client
import os
import pytest
import sys
import asyncio

sys.path.append("./src")

from db_api import postgres_api  # noqa
db_settings = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password'),
    'database': os.getenv('POSTGRES_DB', 'postgres')
}


@pytest.fixture
def postgres_connection():
    conn = psycopg2.connect(**db_settings)
    yield conn
    conn.close()


@pytest.fixture
def qdrant_connection():
    qdrant = qdrant_client.QdrantClient(
        host=os.getenv('QDRANT_HOST', 'localhost'),
        port=os.getenv('QDRANT_PORT', '6333')
    )
    yield qdrant
    qdrant.close()


def test_postgres_connection():
    conn = postgres_connection
    assert conn is not None


def test_qdrant_connection():
    qdrant = qdrant_connection
    assert qdrant is not None


def test_get_user():
    user = asyncio.run(postgres_api.get_user_test())
    print(user)
    assert user is not None
    assert 'id' in user
    assert 'name' in user
    assert 'info' in user
