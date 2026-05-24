# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose the ports the honeypot listens on
# Default SSH port: 2222
# Default HTTP port: 8080
EXPOSE 2222 8080

# Run honeypot.py when the container launches
# Using -u to ensure logs are flushed to stdout/stderr immediately
CMD ["python", "-u", "honeypot.py"]
