#!/bin/bash

# packages
# - docker (by standard repo)
	sudo apt install docker.io

# connect disk
    sudo mkdir /media/usbdata
    sudo chmod 777 /media/usbdata -R
    # Test
    sudo mount -t ext4 /dev/sda1 /media/usbdata/  
    mount | grep /dev/sd
    sudo umount /dev/sda1
    # fstab
    sudo /bin/sh -c 'echo "LABEL=usbdata /media/usbdata ext4 auto,nofail 0 0" >> /etc/fstab'
        * geen ‘defaults’, maar ‘auto,nofail’: hiermee start de server door als de usb-schijf tijdens opstarten niet aanwezig is’
    sudo mount -a
    controleren met: reboot + mount
    # Mappen aanmaken en rechten
    sudo mkdir /media/usbdata/user/Publiek
    sudo mkdir /media/usbdata/user/Publiek\Downloads # ?
    sudo mkdir /media/usbdata/user/Publiek\Muziek
    sudo chmod 777 /media/usbdata/user/Publiek -R

# crontab
# - upgrade

# check if config folder already exist; if so, skip copying
# else:
# - config/lms => /media/usbdata/config/docker/lms
# - config/transmission => /media/usbdata/config/docker/transmission

# copy rc.local file
# - rc.local => /etc

# make rc.local executable
    sudo chmod +x /etc/rc.local
    sudo systemctl status rc-local  # Check status

# - execute /etc/rc.local to monitor docker installation proces (can be tedious)

# - reboot
