from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv
load_dotenv(".env")

client = QdrantClient(
    host=os.environ["QDRANT_HOST"], port=os.environ["QDRANT_PORT"])
try:
    client.create_collection("memories", vectors_config=models.VectorParams(
        size=1536, distance=models.Distance.COSINE))
except Exception as e:
    print(e)
    pass
