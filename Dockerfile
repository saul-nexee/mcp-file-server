FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir "mcp[cli]"

# Copy the server code
COPY server.py /app/

# Create a directory to mount the local files
RUN mkdir /data

# Command to run the server
CMD ["python", "server.py"]