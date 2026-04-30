FROM python:3.10-slim

WORKDIR /app
COPY sdk/python /app/sdk/python
RUN pip install -e /app/sdk/python

COPY demo/producer /app/demo/producer

CMD ["python", "demo/producer/app.py"]
