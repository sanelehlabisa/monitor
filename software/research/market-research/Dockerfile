FROM python:3.14-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY pipeline.py send_due_messages.py ./
CMD ["python", "send_due_messages.py", "--mock-sms-api", "--mock-sms-bind", "0.0.0.0", "--mock-sms-port", "8080"]
