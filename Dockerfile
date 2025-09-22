FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt gunicorn

COPY app/ /app/app
COPY wsgi.py /app/wsgi.py
ENV PYTHONPATH=/app

# Gunicorn binds 5000 inside container
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "app:create_app()"]

# Flat /health inside container (no external prefix)
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2).getcode()==200 else 1)"
