FROM python:3.13-slim

WORKDIR /app

COPY ingestion/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ingestion /app/ingestion

CMD ["python", "-m", "ingestion.app.jobs.scheduler"]
