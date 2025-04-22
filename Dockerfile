# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Ensure output is immediately flushed to the terminal
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the bot when the container launches
CMD ["python", "app/main.py"]