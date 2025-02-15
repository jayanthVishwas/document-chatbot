# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining backend files
COPY . .

RUN python -m openai migrate

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to start FastAPI
CMD ["uvicorn", "main_websockets:app", "--host", "0.0.0.0", "--port", "8000"]