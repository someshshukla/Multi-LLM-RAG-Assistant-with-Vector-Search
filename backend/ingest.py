import os
import argparse
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from typing import List

# We use an open-source, local embedding model to save costs
# BGE-m3 or all-MiniLM-L6-v2 are great free choices.
class LocalHuggingFaceEmbeddings:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
        
    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

# Mock function simulating Gemini 1.5 Pro multimodal table extraction
def extract_tables_with_gemini(page_content: str) -> str:
    # In a real scenario, you pass the PDF page image to Gemini 1.5 Pro
    # and ask: "Extract all tables in this image to Markdown format."
    # Here we mock that behavior.
    if "table" in page_content.lower() or "revenue" in page_content.lower():
        return "\n\n| Extracted Table | Value |\n|---|---|\n| Revenue | $10M |\n| Growth | 20% |\n\n"
    return ""

def process_documents(pdf_path: str):
    print(f"Loading PDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"File {pdf_path} not found. Please place a sample PDF.")
        return
        
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    print(f"Extracted {len(pages)} pages. Running Multimodal parsing...")
    enhanced_docs = []
    
    for page in pages:
        # Simulate multimodal extraction
        table_markdown = extract_tables_with_gemini(page.page_content)
        # Append the extracted markdown to the page content
        enhanced_content = page.page_content + table_markdown
        enhanced_docs.append(Document(page_content=enhanced_content, metadata=page.metadata))

    print("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(enhanced_docs)
    
    print(f"Created {len(chunks)} chunks. Generating local embeddings and pushing to pgvector...")
    
    CONNECTION_STRING = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:password@localhost:5432/rag_db"
    )
    COLLECTION_NAME = "financial_reports"
    
    embeddings = LocalHuggingFaceEmbeddings()
    
    # Initialize PGVector
    vectorstore = PGVector.from_documents(
        embedding=embeddings,
        documents=chunks,
        collection_name=COLLECTION_NAME,
        connection=CONNECTION_STRING,
        pre_delete_collection=True, # Overwrite for testing
    )
    
    print("Ingestion complete! Data successfully loaded into local pgvector.")

if __name__ == "__main__":
    # Create a dummy PDF if none exists for demo purposes
    dummy_pdf = "sample_10k.pdf"
    if not os.path.exists(dummy_pdf):
        print("Creating a dummy 'sample_10k.pdf' to demonstrate pipeline...")
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(dummy_pdf)
        c.drawString(100, 750, "Financial Statement 2026")
        c.drawString(100, 730, "The company achieved strong revenue growth.")
        c.drawString(100, 710, "Our AI pipelines reduced COGS by 15%.")
        c.save()
        
    process_documents(dummy_pdf)
