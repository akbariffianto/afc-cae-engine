FROM python:3.10-slim

EXPOSE 7860

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

WORKDIR /app

COPY --chown=user requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt

COPY --chown=user . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
