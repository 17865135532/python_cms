#!/bin/bash
pkill -9 gunicorn
gunicorn -c gunicorn.py manage:app
