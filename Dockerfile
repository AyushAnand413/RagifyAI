FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/tmp/.huggingface \
    SENTENCE_TRANSFORMERS_HOME=/tmp/.cache/sentence-transformers \
    NLTK_DATA=/usr/local/nltk_data

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        poppler-utils \
        tesseract-ocr \
        libtesseract-dev \
        libleptonica-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*


RUN tesseract --version


COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt


# FINAL NLTK INSTALL FIX
RUN mkdir -p /usr/local/nltk_data && \
    python -m nltk.downloader -d /usr/local/nltk_data punkt && \
    python -m nltk.downloader -d /usr/local/nltk_data punkt_tab && \
    python -m nltk.downloader -d /usr/local/nltk_data averaged_perceptron_tagger && \
    python -m nltk.downloader -d /usr/local/nltk_data averaged_perceptron_tagger_eng && \
    python -m nltk.downloader -d /usr/local/nltk_data wordnet


COPY . /app

EXPOSE 7860

CMD ["sh", "-c", "python -m flask --app web_app:app run --host 0.0.0.0 --port ${PORT:-7860}"]
