#!/usr/bin/sh
# you can use this to easily update your src code and restart the apps
# 1. git pull latest code from github (assuming git ssh pub key is set)
# 2. stop all processes of the app group
# 3. start all processes of the app group
APPGROUP=PYTAVIA-APP
GITBRANCH=staging           # git branch to pull from
APPENV=staging              # env to run the app

# go to the current directory of the script
cd "$(dirname "${BASH_SOURCE[0]}")"

# update source code
git switch -c $GITBRANCH || git switch $GITBRANCH
git pull --rebase origin $GITBRANCH

# stop all processes
sh /opt/blipcom/software/cimb/cimb-eodf-secure/stop-pytavia-web.sh
sh /opt/blipcom/software/cimb/cimb-eodf-secure/stop-pytavia-event.sh

# start all processes
sh /opt/blipcom/software/cimb/cimb-eodf-secure/start-pytavia-web.sh $APPENV
sh /opt/blipcom/software/cimb/cimb-eodf-secure/start-pytavia-event.sh $APPENV

printf "\n#####################################################\n"
printf "\nAll $APPGROUP ($APPENV) processes has been started ...\n"
printf "\n#####################################################\n"