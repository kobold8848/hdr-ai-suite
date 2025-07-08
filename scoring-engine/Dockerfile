FROM python:3.11-slim

# ---------- ① 安装 ffmpeg（用于 hdrgainmap） ----------
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .

CMD ["uvicorn", "scorer:app", "--host", "0.0.0.0", "--port", "8500"]
