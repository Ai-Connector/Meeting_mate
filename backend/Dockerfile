# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code to the working directory
COPY . .

# Make port 50051 available to the world outside this container
EXPOSE 50051

# Define environment variable
ENV PYTHONUNBUFFERED 1

# Run server.py when the container launches
CMD ["python", "server.py"]
