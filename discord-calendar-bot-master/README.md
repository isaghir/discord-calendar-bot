# Discord Calendar Bot

Iman Saghir & Divya Heballi<br/><br/>

## Adding the Bot to a Server

TODO
<br/><br/>

## Docker

We have used Docker as the means of packaging and running this application.<br/><br/>

### How to build and upload the Docker image

These instructions are for Mac/Linux users.

First ensure you have the following installed:

- Docker
- Access Credentials for an AWS IAM user
- AWS CLI (v1, not v2) installed and configured by running `aws configure` (set default region to eu-west-2)

Then build and push the image to ECR by running the following commands:

${VERSION} is the version number of the image e.g. 1.0.0 (check ECR in the AWS Console to see what the next version

```
eval $(aws ecr get-login --no-include-email)
docker build -t discord-calendar-bot:${VERSION} .
docker tag discord-calendar-bot:${VERSION} 581391028770.dkr.ecr.eu-west-2.amazonaws.com/discord-calendar-bot:${VERSION}
docker push 581391028770.dkr.ecr.eu-west-2.amazonaws.com/discord-calendar-bot
```

### Running the bot locally

Once you have built the Docker image you can just execute `docker run -it discord-calendar-bot:${VERSION}`
