FROM python:3.10-slim

WORKDIR /app
COPY sdk/python /app/sdk/python
RUN pip install -e /app/sdk/python

COPY demo/consumer /app/demo/consumer

CMD ["python", "demo/consumer/app.py"]
