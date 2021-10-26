#!/usr/bin/sh
# use the same APPNAME in stop-pytavia-web.sh
APPNAME=PYTAVIA
HOST=localhost
PORT=49000

# ./start-pytavia-web.sh production 
if [ ! -z "$1" ] && [ $1 = "production" ]; then
    export FLASK_ENV=production
    CORES=`getconf _NPROCESSORS_ONLN`
    WORKERS=$((CORES*2+1))
    pip install gunicorn
    nohup gunicorn -n $APPNAME -b $HOST:$PORT -w $WORKERS server:app >> pytavia.out 2>&1 &
    printf "\nApplication $APPNAME has been started ...\n"

# ./start-pytavia.sh
else
    export FLASK_APP=server.py
    export FLASK_ENV=development
    flask run --host=$HOST --port=$PORT

fi
