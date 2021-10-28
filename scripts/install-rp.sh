#!/bin/bash
#
# This script will install RP Music Server onto a fresh copy of Rapsbian OS Lite
#

if [ -z "$(whoami | grep root)" ]
then
    echo "Not running as root."
    echo "Script ended with failure."
    exit
fi

echo "Installing docker.io packages."
if [ ! $(dpkg --list | grep docker.io | awk '{print $1}' | grep ii) ]; then 
	apt install docker.io -y
fi

echo "Creating mountpoint for harddisk."
if [ ! -d /media/usbdata ]; then
    mkdir /media/usbdata
    chmod 777 /media/usbdata -R
fi

echo "Adding line to /etc/fstab."
if [ ! $(grep "LABEL=usbdata" /etc/fstab) ]; then
    # auto,nofail: server start even when harddisk is not present
    #/bin/sh -c 'echo "LABEL=usbdata /media/usbdata ext4 auto,nofail 0 0" >> /etc/fstab'
    echo "Hello"
fi    
mount -a

echo "Creating user directories."
mkdir /media/usbdata/user/Publiek -p
mkdir /media/usbdata/user/Publiek\Downloads -p
mkdir /media/usbdata/user/Publiek\Muziek -p
chmod 777 /media/usbdata/user/Publiek -R

echo "Adding line to /etc/crontab."
if [ $(grep "dist-upgrade" /etc/crontab) ]; then
    #/bin/sh -c 'echo "02 10 * * * root apt dist-upgrade" >> /etc/crontab'
    echo "Hello2"
fi

# check if config folder already exist; if so, skip copying
# else:
# - config/lms => /media/usbdata/config/docker/lms
# Ask if transmission should be installed (Transmission docker-container will not be started in rc.local in config files are not present)
# - config/transmission => /media/usbdata/config/docker/transmission

# copy rc.local file
# - rc.local => /etc

# make rc.local executable
chmod +x /etc/rc.local
#    sudo systemctl status rc-local  # Check status

# Execute /etc/rc.local to monitor docker installation proces (can be tedious)
echo "Start executing /etc/rc.local..."
/etc/rc.local
echo "Done executing /etc/rc.local."

echo "Installation complete, system will be rebooted."
reboot now
