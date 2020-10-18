#!/bin/bash
week=$(date +%U)
if [ $(($week % 2)) == 0 ]; then 
    echo even week no email
else 
    /home/pi/AutoJornal/env/bin/python /home/pi/AutoJornal/main.py
    echo odd week sent email
fi
