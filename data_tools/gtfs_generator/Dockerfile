FROM python:3.11-slim

WORKDIR /app

# No external dependencies currently, but good practice to have requirements ready
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY gtfs_generator.py .

CMD ["python", "gtfs_generator.py"]
