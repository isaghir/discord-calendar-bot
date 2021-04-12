# Base image - has python 3.8 installed on buster debian OS.
FROM python:3.8-slim-buster  

# Copy all the code files onto the image at path /bot (on the docker image)
COPY . /bot  
# Set the working directory to /bot (means all commands are now executed in that directory)
WORKDIR /bot  
 #Install all the packages listed in the requirements file
RUN pip install -r requirements.txt  
# This environment variable ensured python output is sent to the console
ENV PYTHONUNBUFFERED=1
 # The command to execute when the bot is run
CMD ["python", "bot.py"] 

