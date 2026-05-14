FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system opsight && adduser --system --ingroup opsight opsight

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==24.3.1 && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY prompts ./prompts
RUN mkdir -p /app/artifacts/ai-rca && chown -R opsight:opsight /app

USER opsight

EXPOSE 8090

HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8090/health/ready', timeout=2)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
