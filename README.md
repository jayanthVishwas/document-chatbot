# Fullstack-rag-chatbot Using REACT and FAST API

A full-stack chatbot application that leverages React for the frontend and Python (FastAPI) for the backend with WebSocket support for real-time communication. The chatbot uses Pinecone for vector storage and OpenAI for generating responses based on user queries and PDFs.

# Repository Structure

This repository contains two main folders:

**rag-pdf-chatbot-frontend**: The React frontend for the chatbot.<br>
**rag-pdf-chatbot-backend**: The Python backend using FastAPI for handling WebSocket connections and processing queries.

# Features
**Frontend**: Real-time chat interface built with React, customizable chat bubbles, file upload support. <br>
**Backend**: WebSocket server using FastAPI, PDF text extraction, text embedding using OpenAI, context-based response generation using Pinecone VectorDB.

# Prerequisites

Node.js (v14.x or later) <br>
npm (v6.x or later) <br>
Python (v3.8 or later) <br>

# Installation Instructions

# 1. Clone the repository
git clone https://github.com/jayantraj/fullstack-rag-chatbot.git <br>
cd fullstack-rag-chatbot <br>

# 2. Setup Frontend
cd rag-pdf-chatbot-frontend <br>
npm install <br>
npm start <br>

**The frontend should now be running on http://localhost:3000.** <br>

# 3. Setup Backend
cd ../rag-pdf-chatbot-backend <br>
pip install -r requirements.txt <br>

**Create a .env file in the rag-pdf-chatbot-backend directory and add your API keys** <br>

PINECONE_API_KEY=your_pinecone_api_key <br>
OPENAI_API_KEY=your_openai_api_key  <br>

**Start the backend server with uvicorn** <br>
uvicorn main_websockets:app --host 0.0.0.0 --port 8000 --reload <br>

**The backend should now be running on http://localhost:8000.**<br>

# 4. Connecting Frontend and Backend
Ensure both the frontend and backend servers are running. <br>
The frontend (React app) will connect to the backend via WebSocket at ws://localhost:8000/ws. <br>


# 5. CI/CD Pipeline

This project uses a Continuous Integration and Continuous Deployment (CI/CD) pipeline to ensure smooth and automated building, testing, and deploying of the application. The pipeline is built using GitHub Actions and Docker.

## Overview of the CI/CD Pipeline:

1. **Triggered on Push**:
   The pipeline is triggered automatically whenever code is pushed to the `main` branch.

2. **Frontend Setup**:
   - The Node.js environment is set up.
   - Firebase environment variables for the frontend are set using GitHub secrets.
   - Frontend dependencies are installed, and the app is built using `npm run build`.

3. **Backend Setup**:
   - Python environment is set up with version 3.9.
   - Backend dependencies are installed from the `requirements.txt` file.
   - Environment variables, such as the OpenAI API key and Pinecone API key, are set using GitHub secrets.

4. **Testing**:
   - Backend tests are run using `pytest` to ensure the backend functions correctly.
   
5. **Docker Image Building and Pushing**:
   - Docker images for both the frontend and backend are built.
   - The images are tagged and pushed to Docker Hub.


# Demo

https://github.com/user-attachments/assets/6d5f72a9-3ddd-43fe-b3e7-865cc8f6698c




