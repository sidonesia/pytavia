#!/usr/bin/sh
# use the same APPNAME in stop-pytavia-web.sh
APPNAME=PYTAVIA
HOST=localhost
PORT=49000
VENVDIR="venv"  # "venv" or empty if not using a python env

# ./start-pytavia-web.sh production 
# ./start-pytavia-web.sh staging 
# ./start-pytavia-web.sh development 
if [ ! -z "$1" ]; then
    # go to the current directory of the script
    cd "$(dirname "${BASH_SOURCE[0]}")"

    # use virtualenv if defined
    if [ ! -z "$VENVDIR" ]; then
        # create virtualenv if not found
        if [ ! -d "$VENVDIR" ]; then
            python3 -m venv $VENVDIR
        fi

        # activate virtualenv
        . $VENVDIR/bin/activate

        # install dependencies
        pip install -r requirements.txt
    fi

    if [ $1 = "production" ]; then
        export FLASK_ENV=production
        export CONF_FILE="app-production.conf"

    elif [ $1 = "staging" ]; then   
        export FLASK_ENV=development
        export CONF_FILE="app-staging.conf"

    elif [ $1 = "development" ]; then   
        export FLASK_ENV=development
        export CONF_FILE="app-dev.conf"

    else
        export FLASK_ENV=development
        export CONF_FILE="app-running.conf"
    fi

    # by default, only run gunicorn in production
    if [ $1 = "production" ]; then
        CORES=`getconf _NPROCESSORS_ONLN`
        WORKERS=$((CORES*2+1))
        pip install gunicorn
        nohup gunicorn -n $APPNAME -b $HOST:$PORT -w $WORKERS server:app >> pytavia.out 2>&1 &
    else
        export FLASK_APP=server.py
        nohup flask run --host=$HOST --port=$PORT >> pytavia.out 2>&1 &
    fi
    printf "\n#########################################\n"
    printf "\nApplication $APPNAME has been started ...\n"
    printf "\n#########################################\n"

# ./start-pytavia.sh
else
    export FLASK_APP=server.py
    export FLASK_ENV=development
    flask run --host=$HOST --port=$PORT

fi