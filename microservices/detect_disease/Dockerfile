# Pull base image
FROM python:3.11-alpine

# Set work directory
WORKDIR /app/microservices/detect_disease

# Copy requirements
COPY ./requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6  -

# Copy code
COPY . .
