# Fullstack RAG PDF chatbot Using REACT and FAST API

A full-stack chatbot application that leverages React for the frontend and Python (FastAPI) for the backend with WebSocket support for real-time communication. The chatbot uses Pinecone for vector storage and OpenAI for generating responses based on user queries and PDFs and Redis for caching prompts and responses.

Application Hosted: http://3.82.47.188:3000/

# Repository Structure

This repository contains two main folders:

**frontend**: The React frontend for the chatbot.<br>
**backend**: The Python backend using FastAPI for handling WebSocket connections and processing queries.

# Features
**Frontend**: Real-time chat interface built with React, customizable chat bubbles, file upload support. <br>
**Backend**: WebSocket server using FastAPI, PDF text extraction, text embedding using OpenAI, context-based response generation using Pinecone VectorDB and Redis for caching. 

# Installation Instructions

## 1. Clone the repository
```bash
git clone https://github.com/jayanthVishwas/document-chatbot.git 
```

## 2. Create a .env file in the root directory and add API keys for Open API, Pinecone and Upstash Redis
```bash
PINECONE_API_KEY=your_pinecone_api_key 
OPENAI_API_KEY=your_openai_api_key 
UPSTASH_REDIS_ENDPOINT=your_redis_endpoint 
UPSTASH_REDIS_TOKEN=your_redis_token 
```

## 3. Run Docker Compose
   ```bash
   docker-compose up --build
   ```

**The application should now be running on http://localhost:3000.** <br>

# Setting up AWS Infrastructure using Terraform

This Terraform configuration creates a simple AWS setup that includes:
- A VPC with a CIDR block of `10.0.0.0/16`
- An Internet Gateway attached to the VPC
- A Public Subnet with auto-assign public IP enabled
- A Route Table that routes outbound traffic (`0.0.0.0/0`) to the Internet Gateway
- A Security Group allowing inbound SSH (port **22**) and HTTP (port **8000**) and HTTP (port **3000**)
- An EC2 Instance using a specified AMI, instance type, and with a public IP address assigned
- An Output that shows the public IP of the EC2 instance

## Prerequisites
- **Terraform** installed on your system

## Usage
1. **Change directory** to `infra`  
   ```bash
   cd infra
   ```

2. Initialize Terraform: 
   ```bash
   terraform init
   ```

3. Review the plan: 
   ```bash
   terraform plan
   ```

4. Apply the configuration to create resources in AWS: 
   ```bash
   terraform apply
   ```

5. To clean up (and stop incurring AWS costs), run: 
   ```bash
   terraform destroy
   ```


