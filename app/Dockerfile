FROM python:3.12

COPY requirements.txt /app/
RUN apt-get update && \
    apt-get install -y unixodbc-dev gcc g++ libpq-dev odbc-postgresql && \
    pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
COPY app.py /app/

EXPOSE 8080

CMD ["python", "app.py"]
