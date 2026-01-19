#!/bin/sh

gunicorn -w 4 "main:app" -b 0.0.0.0:5000 -t 0 --graceful-timeout 5 --worker-class gevent --workers 4
