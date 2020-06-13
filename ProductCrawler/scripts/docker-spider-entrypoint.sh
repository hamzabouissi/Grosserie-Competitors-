#!/bin/bash
./scripts/run.sh

if [ ! -e env ]
then
  virtualenv env --python=python3
fi
source ./env/bin/activate
pip install -r requirements.txt

echo "20 * * * * /bin/bash $filepath > /tmp/logs.log 2>&1" > scheduler.txt
crontab scheduler.txt
cron -f