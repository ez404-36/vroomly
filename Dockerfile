FROM python:3.13-slim

RUN apt-get update
RUN pip install uv

WORKDIR /app

COPY pyproject.toml /app/

RUN uv pip install --system --no-cache-dir -e /app

COPY . /app

CMD ["python", "main.py"]
