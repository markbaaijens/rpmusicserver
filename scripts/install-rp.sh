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

echo "Installing docker.io packages:"
if [ ! $(dpkg --list | grep docker.io | awk '{print $1}' | grep ii) ]; then 
	apt-get install docker.io -y
    echo " => package docker.io is installed"
else
    echo " => package docker.io is already installed."
fi

echo "Creating mountpoint for harddisk:"
if [ ! -d /media/usbdata ]; then
    mkdir /media/usbdata
    chmod 777 /media/usbdata -R
    echo " => mountpoint created."    
else
    echo " => mountpoint is already present."    
fi

echo "Adding line to /etc/fstab:"
if [ ! "$(grep "LABEL=usbdata" /etc/fstab)" ]; then
    # auto,nofail: server start even when harddisk is not present
    /bin/sh -c 'echo "LABEL=usbdata /media/usbdata ext4 auto,nofail 0 0" >> /etc/fstab'
    echo " => line added."
else
    echo " => line is already present."    
fi    
mount -a

echo "Creating user directories."
mkdir /media/usbdata/user/Publiek -p
mkdir /media/usbdata/user/Publiek/Downloads -p
mkdir /media/usbdata/user/Publiek/Muziek -p
chmod 777 /media/usbdata/user/Publiek -R

echo "Adding line to /etc/crontab:"
if [ ! "$(grep "dist-upgrade" /etc/crontab)" ]; then
    /bin/sh -c 'echo "02 10 * * * root apt dist-upgrade" >> /etc/crontab'
    echo " => line added."    
else
    echo " => line is already present."    
fi

# check if config folder already exist; if so, skip copying
echo "Copy config files"
if [ ! -d /media/usbdata/config ]; then
    mkdir -p /media/usbdata/config/docker
    cp -r /tmp/rpmusicserver/files/config/* /media/usbdata/config/docker
    echo " => config files copied."    
else
    echo " => config folder is already present, no config files copied."    
fi

cp /tmp/rpmusicserver/files/rc.local /etc
chmod +x /etc/rc.local

# Execute /etc/rc.local to monitor docker installation proces (can be tedious)
echo "Start executing /etc/rc.local..."
/etc/rc.local
echo "Done executing /etc/rc.local."

echo "Installation complete, system will be rebooted."
reboot now
