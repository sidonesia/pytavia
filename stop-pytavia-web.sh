#!/usr/bin/sh
# use the same APPNAME, HOST, PORT in start-pytavia-web.sh
APPNAME=PYTAVIA
HOST=localhost
PORT=49000

printf "\n#########################################\n"
pkill -f "flask run --host=$HOST --port=$PORT" && printf "\nApplication $APPNAME has been stopped ...\n"
pkill -f "gunicorn -n $APPNAME" && printf "\nApplication $APPNAME has been stopped ...\n"
printf "\n#########################################\n"