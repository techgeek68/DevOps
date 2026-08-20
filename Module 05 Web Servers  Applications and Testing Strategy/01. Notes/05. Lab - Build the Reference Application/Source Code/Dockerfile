# Dockerfile — isolated build, identical on laptop and CI
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
EXPOSE 8000
# Stateless process, config from env, port from env, logs to stdout
CMD ["gunicorn", "-b", "0.0.0.0:8000", "refapp.app:create_app()"]
