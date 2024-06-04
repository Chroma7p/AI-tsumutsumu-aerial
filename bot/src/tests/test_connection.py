import psycopg2
import qdrant_client
import os
import pytest

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
