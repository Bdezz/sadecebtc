FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "src/xmr_bot.py"]

