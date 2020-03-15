#!/bin/bash

export NCKU_USERNAME="F04066028"
export NCKU_PASSWORD="*********"
export GMAIL_USERNAME="EthanM92F@gmail.com"
export GMAIL_PASSWORD="********"
cd /Users/ethanchan/Desktop/MyPythonProjects/grade_notify
source venv/bin/activate
python3 grade_notify.py
sleep 10s
deactivate
cd
