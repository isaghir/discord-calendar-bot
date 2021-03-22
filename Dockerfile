FROM python:3.8-slim-buster

COPY . /bot
WORKDIR /bot

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]