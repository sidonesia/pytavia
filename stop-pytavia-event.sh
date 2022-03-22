#!/usr/bin/sh
# use the same APPNAME in start-pytavia-event.sh
APPNAME=PYTAVIA-EVT

KILLPID=`ps -ef | grep $APPNAME | grep -v grep | gawk '{ print $2}'`
kill $KILLPID

printf "\n#########################################\n"
printf "\nApplication $APPNAME ($KILLPID) has been stopped ...\n"
printf "\n#########################################\n"
