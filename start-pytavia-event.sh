#!/usr/bin/sh
# use the same APPNAME in stop-pytavia-event.sh
APPNAME=PYTAVIA-EVT
VENVDIR="venv"  # or empty if not using a python env

# sample usage
# ./start-pytavia-event.sh
# ./start-pytavia-event.sh development 
# ./start-pytavia-event.sh staging 
# ./start-pytavia-event.sh production 
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
fi

nohup python3 server-event-processor.py $APPNAME >> event-processor.out 2>&1 &

printf "\n#########################################\n"
printf "\nApplication $APPNAME has been started ...\n"
printf "\n#########################################\n"