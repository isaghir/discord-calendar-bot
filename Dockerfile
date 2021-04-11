FROM python:3.8-slim-buster  # Base image - has python 3.8 installed on buster debian OS.

COPY . /bot  # Copy all the code files onto the image at path /bot (on the docker image)
WORKDIR /bot  # Set the working directory to /bot (means all commands are now executed in that directory)

RUN pip install -r requirements.txt  # Install all the packages listed in the requirements file

ENV PYTHONUNBUFFERED=1  # This environment variable ensured python output is sent to the console
CMD ["python", "bot.py"]  # The command to execute when the bot is run

