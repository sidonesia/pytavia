#!/usr/bin/sh
# use the same APPNAME in start-pytavia-event.sh
APPNAME=PYTAVIA-EVT

KILLPID=`ps -ef | grep $APPNAME | grep -v grep | gawk '{ print $2}'`
kill $KILLPID
echo "process $KILLPID has been stopped ..."
