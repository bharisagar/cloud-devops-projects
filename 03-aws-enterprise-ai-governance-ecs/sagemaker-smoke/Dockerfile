FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/program

COPY serve.py .

EXPOSE 8080

ENTRYPOINT ["python", "/opt/program/serve.py"]
