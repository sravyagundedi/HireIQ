FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg gcc libsndfile1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
RUN mkdir -p uploads reports

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
