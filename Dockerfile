FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/tmp/.huggingface \
    SENTENCE_TRANSFORMERS_HOME=/tmp/.cache/sentence-transformers

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1 \
      libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt

COPY . /app

EXPOSE 7860

CMD ["sh", "-c", "python -m flask --app web_app:app run --host 0.0.0.0 --port ${PORT:-7860}"]
