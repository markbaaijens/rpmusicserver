#!/bin/bash

if [ -z "$(whoami | grep root)" ]
then
    echo "Not running as root."
    exit
fi

sourcefolder=$(jq '.sourcefolder' /media/usbdata/config/transcoder-settings.json | tr -d '"')
oggfolder=$(jq '.oggfolder' /media/usbdata/config/transcoder-settings.json | tr -d '"')
mp3folder=$(jq '.mp3folder' /media/usbdata/config/transcoder-settings.json | tr -d '"')

# TODO Testing
if [ -z $sourcefolder ]; then
    exit
fi

python3 /usr/local/bin/transcoder/transcoder.py --settingsfile /media/usbdata/config/transcoder-settings.json --verbose --logfolder "/media/usbdata/config"

# TODO This needs soem more testing
if [ -z $mp3folder ]; then
    chmod 777 $mp3folder/* -R -f
fi
if [ -z $oggfolder ]; then
    chmod 777 $oggfolder/* -R -f
fi
