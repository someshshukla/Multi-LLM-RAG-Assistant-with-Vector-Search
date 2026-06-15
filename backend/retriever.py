from langchain_postgres.vectorstores import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

import os

CONNECTION_STRING = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:password@localhost:5432/rag_db"
)
COLLECTION_NAME = "financial_reports"

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Connect to the pgvector instance
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
    use_jsonb=True,
)

def hybrid_search(query: str, k: int = 4):
    """
    Performs a vector search (dense). 
    In a full production scenario, we would also run a BM25 query 
    against a Full-Text Search index in Postgres and merge results (RRF).
    """
    try:
        # Standard dense vector retrieval
        docs = vectorstore.similarity_search(query, k=k)
        
        # Here we would normally pass the combined BM25 + Dense results 
        # through a local Cross-Encoder for re-ranking.
        
        results = []
        for d in docs:
            results.append({
                "content": d.page_content,
                "metadata": d.metadata
            })
        return results
    except Exception as e:
        print(f"Error during retrieval: {e}")
        # Fallback if DB isn't running yet during dev
        return [
            {"content": "Fallback: The DB is offline. In 2026, revenue grew by 20%.", "metadata": {}}
        ]
