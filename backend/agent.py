import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from retriever import hybrid_search

# Load environment variables from .env file
load_dotenv()

# Using Groq for fast routing and generation. (Compatible with vLLM OpenAI endpoint)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your-groq-api-key")

def process_query(query: str):
    trace = []
    
    trace.append({"step": "Received Query", "details": query})
    
    # 1. Router Logic: Is this a general question or needs Vector DB?
    # For now, we simulate the routing decision.
    use_rag = True
    
    if use_rag:
        trace.append({"step": "Router Decision", "details": "Routed to Vector DB (RAG) for domain knowledge."})
        
        # 2. Retrieve context using Hybrid Search
        docs = hybrid_search(query)
        context = "\n".join([doc["content"] for doc in docs])
        trace.append({"step": "Retrieval", "details": f"Retrieved {len(docs)} documents."})
        
        # 3. Generate Answer
        llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")
        system_prompt = f"Answer the user based on the following context:\n{context}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        # Call the actual Groq API to generate the response
        response = llm.invoke(messages)
        response_text = response.content
        
        trace.append({"step": "Generation", "details": "Generated answer using LLaMA 3 via Groq."})
        
    else:
        trace.append({"step": "Router Decision", "details": "Routed to general knowledge / calculator."})
        response_text = "Calculated/General response."

    return response_text, trace
