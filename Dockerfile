# Dockerfile for the FastAPI backend

# 1. Base Image: Start with an official Python base image.
# Using a slim version reduces the image size. Specify a Python version.
FROM python:3.9-slim

# 2. Set Environment Variables (Optional but good practice)
ENV PYTHONUNBUFFERED=1    # Ensures Python output (e.g., print statements) is sent straight to the terminal
ENV PYTHONDONTWRITEBYTECODE=1 # Prevents Python from writing .pyc files to disc (not needed in container)

# 3. Set Working Directory: Define the working directory inside the container.
WORKDIR /app_code 
# All subsequent commands (COPY, RUN, CMD) will be relative to this directory.

# 4. Copy Requirements First & Install Dependencies:
# This step is crucial for Docker layer caching. If requirements.txt doesn't change,
# Docker can reuse this layer, speeding up subsequent builds.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code: Copy the 'app' directory from your project
# (containing main.py, chatbot_service.py, etc.) into the WORKDIR/app.
# We'll map it to an 'app' subdirectory inside /app_code for clarity.
COPY ./app ./app

# 6. Expose Port: Inform Docker that the container listens on port 8000 at runtime.
# This doesn't actually publish the port; that's done with `docker run -p`.
EXPOSE 8000

# 7. Define the Command to Run the Application:
# This is the command that will be executed when the container starts.
# We run uvicorn, making it listen on all available network interfaces (0.0.0.0)
# inside the container, on port 8000.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]