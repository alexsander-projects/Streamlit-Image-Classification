FROM python:3.10

WORKDIR /app

EXPOSE 8501
EXPOSE 6379

RUN apt-get update

COPY requirements.txt .
COPY redis.conf .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY main.py .

ENTRYPOINT ["streamlit", "run", "main.py"]