FROM python:3.8

WORKDIR /home

ENV TELEGRAM_API_TOKEN="508638850:AAH-6a0MifYdiqU5SqkixWF36bk9rDYqueI"


ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram==2.25 pytz && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./
COPY /res/* ./res/

ENTRYPOINT ["python", "server.py"]

