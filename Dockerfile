# Dùng khi Render để trống Root Directory: build app trong secure-validator-lab
FROM python:3.12-slim
WORKDIR /app
COPY secure-validator-lab/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY secure-validator-lab/ .
# Render cấp cổng qua biến PORT
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-10000} app:app"]
