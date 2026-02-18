FROM python:3.11-slim

WORKDIR /app

# Copy the backend application
COPY docs/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docs/backend/app ./app

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
