# Discord Calendar Bot

Iman Saghir & Divya Heballi<br/><br/>

## Commands

| Name                    | Arguments                                                     | Description                                            | Usage                                     |
| ----------------------- | ------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------- |
| add_meeting             | title, date(dd/mm/yyyy), start_time(HH:MM), duration(minutes) | Adds the meeting for this user into the database.      | !add_meeting lecture1 05/04/2021 15:00 60 |
| cancel_meeting          | title, date(dd/mm/yyyy), start_time(HH:MM)                    | Marks the meeting as cancelled.                        | !cancel_meeting lecture1 05/04/2021 15:00 |
| lookup_meeting_by_day   | date(dd/mm/yyyy)                                              | Displays all meetings for the user on the given date.  | !lookup_meeting_by_day 05/04/2021         |
| lookup_meeting_by_week  | None                                                          | Displays all meeting for the user in the next 7 days.  | !lookup_meeting_by_week                   |
| lookup_meeting_by_month | None                                                          | Displays all meeting for the user in the next 30 days. | !lookup_meeting_by_month                  |

<br/>

## Notifications

The bot notifies users when a meeting is about to start.
The bot runs a loop - every minute, a function is run which searches for all meetings starting within the next minute. For each meeting found, a direct message is sent to the user who created it.
<br/><br/>

## Adding the Bot to a Server

If you are a server admin wishing to add this bot, use this link https://discord.com/api/oauth2/authorize?client_id=807309819634647051&permissions=68608&scope=bot
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
<br/><br/>

## Overview of the code

### bot.py

The bot is written using the discord.py library and this file runs the bot which connects to the Discord API. The bot registers with Discord and begins listening to events (user messages etc.) in all the servers and channels it is connected to. The command prefix is set to `!` meaning any message that starts with `!` is interpreted as a command for this bot. Everything following the `!` is the name of the command and the command arguments.

### database.py

The bot uses a database to store information in a meetings table. Every command needs to perform a database query to either create, update, or search for meetings in the database. These queries are wrapped in functions written in database.py.

As well as these commands, this file contains the init_db() function which ensures the database and meetings table exists within postgres RDS instance. This is an idempotent function meaning it can safely run every time the bot starts up and it will always reach the same desired state of database and table existence.

### entrypoint.sh
This is a startup script that Fargate executes when running the container.

