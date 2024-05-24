# Use the official Python image
FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
  gcc \
  libjpeg-dev \
  zlib1g-dev \
  libfreetype6-dev \
  libmagickwand-dev \
  imagemagick \
  redis-tools \
  make \
  && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY ./app /app/app

# Compile the C code
WORKDIR /app/app/c_processing
RUN make

# Return to the app working directory
WORKDIR /app

# Set the PYTHONPATH
ENV PYTHONPATH=/app

# Command to run the FastAPI server with reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
