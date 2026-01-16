FROM python:3.10-slim AS builder

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies with pip cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY app.py mycommands.py params.py bot_config.py db_utils.py ./

FROM python:3.10-slim-buster AS production

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages/
COPY --from=builder /app /app/

# Set Python unbuffered environment variable
ENV PYTHONUNBUFFERED=1

CMD ["python3", "app.py"]
