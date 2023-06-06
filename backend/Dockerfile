# Pull official base image
FROM python:3.9.7-slim-buster

# Set working directory
WORKDIR /app

# Copy the code into the container
COPY . /app

RUN pip install -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Set the command to run the server
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
