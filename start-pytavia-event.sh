#!/usr/bin/sh
# use the same APPNAME in stop-pytavia-event.sh
APPNAME=PYTAVIA-EVT

if [ ! -z "$1" ] && [ $1 = "production" ]; then
    export FLASK_ENV=production
fi
nohup python3 server-event-processor.py $APPNAME >> event-processor.out 2>&1 &
