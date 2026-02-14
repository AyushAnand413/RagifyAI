FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/tmp/.huggingface \
    TRANSFORMERS_CACHE=/tmp/.cache/huggingface/transformers \
    SENTENCE_TRANSFORMERS_HOME=/tmp/.cache/sentence-transformers

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt

COPY . /app

EXPOSE 7860

CMD ["python", "-m", "flask", "--app", "web_app:app", "run", "--host", "0.0.0.0", "--port", "7860"]
