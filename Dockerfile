# 1. Use a lightweight Python image to keep the attack surface small
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system-level dependencies for Pillow and SQLite
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first to leverage Docker's layer caching
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Expose the port Streamlit uses
EXPOSE 8501

# 8. Start the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]