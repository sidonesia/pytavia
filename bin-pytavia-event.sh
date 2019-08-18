#!/usr/bin/sh
nohup python3.7 server-event-processor.py WORKFLOW-PROCESSOR >> event-processor.out 2>&1 &
