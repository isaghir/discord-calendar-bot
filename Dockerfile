FROM python:3.8-slim-buster

COPY . /bot
WORKDIR /bot

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
CMD ["python", "bot.py"]

