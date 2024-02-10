# Stage 1: Build Stage
FROM python:3.8 as builder

WORKDIR /app

# Copy only the requirements file to take advantage of Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage
FROM python:3.8-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

# Copy the producer and consumer scripts
COPY . ./