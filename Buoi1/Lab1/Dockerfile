FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Render cấp cổng qua biến PORT
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-10000} app:app"]
