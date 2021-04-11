#!/bin/bash
# This is a startup script that Fargate executes when running the container.

set -ex #sets bash scripting flags to show log lines and to exit on command failure

python bot.py #runs the bot.py file

