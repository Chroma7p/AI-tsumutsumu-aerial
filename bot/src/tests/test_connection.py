import psycopg2
import qdrant_client
import os

from dotenv import load_dotenv
load_dotenv("../.env", override=True)

db_settings = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password'),
    'database': os.getenv('POSTGRES_DB', 'postgres')
}


def test_postgres_connection():
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(result)
    cursor.close()
    conn.close()


def test_qdrant_connection():
    qdrant = qdrant_client.QdrantClient(
        host=os.getenv('QDRANT_HOST', 'localhost'),
        port=os.getenv('QDRANT_PORT', '6333')
    )
    qdrant.close()
