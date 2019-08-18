#!/usr/bin/sh
KILLPID=`ps -ef | grep WORKFLOW | grep -v grep | gawk '{ print $2}'`
kill $KILLPID
echo "process $KILLPID has been stopped ..."
