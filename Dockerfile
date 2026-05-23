# Use an official lightweight Python runtime
FROM python:3.11-slim

# Setting system environment variables to prevent Python from buffering outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for compiling certain Python wheels (like ChromaDB/hnswlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copying only the dependencies list first to leverage Docker's caching mechanism
COPY requirements.txt .

# Install the Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copying the rest of your application code into the container
COPY . .

# Exposing the port that FastAPI will run on
EXPOSE 8000

# use uvicorn to run the FastAPI app, binding to all interfaces and specifying the port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]