# Use Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /bi
RUN mkdir -p /bi/page_configs
RUN mkdir /bi/page_modules
RUN mkdir /bi/.streamlit

# Install system dependencies (optional, based on your packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY side_bar.yaml .
COPY usr.yaml .
COPY arch.jpg .
COPY page_configs ./page_configs/
COPY page_modules ./page_modules/
COPY .streamlit ./streamlit/

# Expose the default Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
