from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent import process_query

app = FastAPI(title="Advanced Agentic RAG API", version="1.0")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change this to your Vercel frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    trace: list[dict]

@app.post("/api/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    try:
        response_text, trace_data = process_query(request.query)
        return QueryResponse(response=response_text, trace=trace_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ingest")
async def ingest_endpoint():
    try:
        import ingest
        import os
        # Create a dummy PDF if none exists for demo purposes
        dummy_pdf = "sample_10k.pdf"
        if not os.path.exists(dummy_pdf):
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(dummy_pdf)
            c.drawString(100, 750, "Financial Statement 2026")
            c.drawString(100, 730, "The company achieved strong revenue growth.")
            c.drawString(100, 710, "Our AI pipelines reduced COGS by 15%.")
            c.save()
            
        ingest.process_documents(dummy_pdf)
        return {"status": "success", "message": "Ingestion complete! Database is populated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
