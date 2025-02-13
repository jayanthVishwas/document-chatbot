import os
import json
from dotenv import load_dotenv
import fitz  # PyMuPDF
import openai
from pinecone import Pinecone, ServerlessSpec
from fastapi import FastAPI, WebSocket, UploadFile, File
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI with the new client-based API
openai_client = openai.OpenAI(api_key=openai_api_key)

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)

# Create a Pinecone index if it doesn't exist
index_name = "multi-rags-pdf-chatbot"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Match the output dimensions of the embeddings
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
index = pc.Index(index_name)

app = FastAPI()

# Increase request size limit to 100MB
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Enables compression

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Match frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Ensures WebSockets work properly
)



# Pydantic model for query request
class QueryRequest(BaseModel):
    query: str

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

# Function to split text into chunks
def split_text(text, max_tokens=600):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_length += len(word) + 1  # +1 for space
        if current_length > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Create OpenAI embeddings using the API
def create_embeddings(text, model="text-embedding-ada-002"):
    response = openai_client.embeddings.create(model=model, input=[text])
    embeddings = response.data[0].embedding  
    return embeddings

# Function to query Pinecone
def query_pinecone(query, top_k=4):
    query_embedding = create_embeddings(query)
    query_response = index.query(vector=query_embedding, top_k=top_k, include_values=False, include_metadata=True)
    return query_response['matches']

# Function to get response from OpenAI
def get_response_from_openai(query, context):
    prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a witty and humorous almighty being, who loves to crack jokes and speak with a touch of divine sass. Your tone is light-hearted, and you often make humorous observations, as if you are a playful deity speaking to mortals."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()  # Access 'content' attribute directly
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")  # Print detailed error message
        return f"An error occurred while fetching the response from OpenAI: {e}"

# defines the websocket route at /ws
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            query_request = json.loads(data)
            query = query_request.get("query", "").strip()
            print(f"Received query: {query}")  # Debugging statement

            if not query:
                await websocket.send_text(json.dumps({"response": "Query cannot be empty."}))
                continue

            results = query_pinecone(query)

            if results and results[0]['score'] >= 0.4:
                context = " ".join([match['metadata']['text'] for match in results if 'metadata' in match and 'text' in match['metadata']])
                response = get_response_from_openai(query, context) if context.strip() else "No relevant context found."
            else:
                response = "I can't answer from the given PDFs."

            await websocket.send_text(json.dumps({"response": response}))

    except WebSocketDisconnect:
        print("⚠️ WebSocket client disconnected")
    except Exception as e:
        print(f"❌ Unexpected WebSocket error: {e}")
    finally:
        await websocket.close()

# FAST API POST Endpoint. User can upload the PDF directly to the backend
@app.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    for file in files:
        pdf_path = f"/tmp/{file.filename}"
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        print("here")
        # Step 1: Extract text from PDF
        text = extract_text_from_pdf(pdf_path)

        # Step 2: Split text into manageable chunks
        chunks = split_text(text, max_tokens=600)

        # Step 3: Create embeddings for each chunk and upsert to Pinecone
        for i, chunk in enumerate(chunks):
            embeddings = create_embeddings(chunk)
            metadata = {"text": chunk}
            index.upsert(vectors=[(f"{pdf_path}_chunk_{i}", embeddings, metadata)])
    
    return {"status": "PDFs processed successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", limit_max_request_size=100_000_000)  # 100MB

