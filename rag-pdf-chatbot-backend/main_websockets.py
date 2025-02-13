import os
import io
import uuid
import json
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Retrieve API keys
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not pinecone_api_key:
    raise Exception("PINECONE_API_KEY is missing. Set it in your environment.")

# Initialize OpenAI API
import openai
openai.api_key = openai_api_key

# Initialize SentenceTransformer for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')  # ✅ Uses 384D embeddings (MiniLM)
embedding_dim = model.get_sentence_embedding_dimension()  # e.g., 384

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)

# Create a Pinecone index if it doesn't exist
index_name = "document-chatbot-collection"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dim,  # ✅ Ensures it matches MiniLM's 384D embeddings
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
index = pc.Index(index_name)

# Initialize FastAPI app
app = FastAPI(title="Document Chatbot Backend with Pinecone and WebSockets")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Match frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# In-memory storage for full documents
documents = {}  # Mapping: doc_id -> {"filename": str, "text": str}


# --- Helper Functions for Text Extraction ---
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file provided as bytes."""
    data_stream = io.BytesIO(file_bytes)
    try:
        reader = PdfReader(data_stream)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    except Exception as e:
        raise Exception(f"Error processing PDF: {e}")


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from a TXT file provided as bytes."""
    try:
        return file_bytes.decode("utf-8").strip()
    except Exception as e:
        raise Exception(f"Error processing text file: {e}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Split text into overlapping chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# --- WebSocket Endpoint for Question Answering ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time question answering."""
    await websocket.accept()
    try:
        # ✅ **Check Pinecone Index for Documents**
        total_vectors = index.describe_index_stats()
        print(f"📌 Pinecone Index Stats: {total_vectors}")

        if total_vectors["total_vector_count"] == 0:
            await websocket.send_text(json.dumps({"response": "No documents are available in Pinecone."}))
            return

        while True:
            data = await websocket.receive_text()
            query_request = json.loads(data)
            query = query_request.get("query", "").strip()
            print(f"🛠️ Received query: {query}")  # Debugging statement

            if not query:
                await websocket.send_text(json.dumps({"response": "Query cannot be empty."}))
                continue

            # ✅ **Encode query & match embedding dimension**
            query_embedding = model.encode(query, normalize_embeddings=True).tolist()
            print(f"📌 Query Embedding Shape: {len(query_embedding)}")  # Should be 384

            query_response = index.query(vector=query_embedding, top_k=5, include_metadata=True)

            if not query_response["matches"]:
                print(f"⚠️ No matches found in Pinecone.")
                await websocket.send_text(json.dumps({"response": "No relevant context found."}))
                continue

            # ✅ **Retrieve the most relevant document chunks**
            top_chunks = [match["metadata"]["chunk"] for match in query_response["matches"] if "chunk" in match["metadata"]]
            print(f"📖 Retrieved Context Chunks: {top_chunks}")

            if not top_chunks:
                await websocket.send_text(json.dumps({"response": "No relevant context found."}))
                continue

            top_context = "\n".join(top_chunks)[:4000]  # Truncate if too long

            # ✅ **Generate answer using OpenAI**
            prompt = f"Context:\n{top_context}\n\nQuestion: {query}\nAnswer:"
            try:

                response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )

                answer = response.choices[0].message.content.strip()

            except Exception as e:
                answer = f"Error calling OpenAI API: {e}"

            await websocket.send_text(json.dumps({"response": answer}))

    except WebSocketDisconnect:
        print("⚠️ WebSocket client disconnected")
    except Exception as e:
        print(f"❌ Unexpected WebSocket error: {e}")
    finally:
        await websocket.close()


# --- Endpoint: Upload Document ---
@app.post("/upload_pdfs/", summary="Upload a document (PDF or TXT)")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    results = []

    for file in files:
        doc_id = str(uuid.uuid4())
        file_extension = file.filename.lower().split('.')[-1]

        if file_extension not in ["pdf", "txt"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or TXT.")

        file_bytes = await file.read()

        # Extract text
        try:
            text = extract_text_from_pdf(file_bytes) if file_extension == "pdf" else extract_text_from_txt(file_bytes)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting text: {e}")

        if not text:
            raise HTTPException(status_code=400, detail="No text extracted from document.")

        # ✅ **Chunk Text**
        chunks = chunk_text(text)
        vectors = []
        for i, chunk in enumerate(chunks):
            vector = model.encode(chunk, normalize_embeddings=True)
            metadata = {"doc_id": doc_id, "chunk": chunk, "filename": file.filename}
            vectors.append((f"{doc_id}-{i}", vector.tolist(), metadata))

        # ✅ **Upsert into Pinecone**
        index.upsert(vectors=vectors)

        results.append({"doc_id": doc_id, "filename": file.filename, "num_chunks": len(chunks)})

    return {"status": "Success", "uploaded_files": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", limit_max_request_size=100_000_000)  # 100MB
