# Use ultra-stable, light slim python runtime image
FROM python:3.10-slim

# Bind the standard port used by Streamlit network router
EXPOSE 8501

# Prevent Python from writing pyc files to disk and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install native system build requirements securely
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Optimize layer caching by copying dependencies first
COPY src/frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all engineering scripts to container space
COPY . .

# Run production runtime container configuration
ENTRYPOINT ["streamlit", "run", "src/frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]