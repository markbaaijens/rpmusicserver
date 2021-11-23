#!/bin/bash
#
# This script will install RP Music Server onto a copy of Rapsbian OS Lite
#

if [ -z "$(whoami | grep root)" ]
then
    echo "Not running as root."
    echo "Script ended with failure."
    exit
fi

echo "Start installing packages..."
apt-get update
apt-get install docker.io python3-pip tree jq -y
echo "Done installing packages."

echo "Creating mountpoint for harddisk:"
if [ ! -d /media/usbdata ]; then
    mkdir /media/usbdata
    chmod 777 /media/usbdata -R
    echo " => mountpoint created."    
else
    echo " => mountpoint is already present."    
fi

echo "Adding line for usbdata-disk to /etc/fstab:"
if [ ! "$(grep "LABEL=usbdata" /etc/fstab)" ]; then
    # auto,nofail: server starts even when harddisk is not present
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

echo "Adding line for upgrade to /etc/crontab:"
if [ ! "$(grep "apt-get upgrade" /etc/crontab)" ]; then
    /bin/sh -c 'echo "02 10 * * * root apt-get upgrade -y" >> /etc/crontab'
    echo " => line added."    
else
    echo " => line is already present."    
fi

echo "Copy LMS config files"
if [ ! -d /media/usbdata/config/docker/lms ]; then
    mkdir -p /media/usbdata/config/docker/lms
    cp -r /tmp/rpmusicserver/files/config/lms/* /media/usbdata/config/docker/lms
    echo " => LMS config files copied."    
else
    echo " => LMS config folder is already present, no config files copied."    
fi

echo "Install python packages for RP Music Server:"
# Note that b/c this script is executed under sudo, pip3 packages are system-wide installed
pip3 install -r /tmp/rpmusicserver/web-interface/requirements.txt 
echo " => python packages installed." 

echo "Install program files for API:"
mkdir -p /usr/local/bin/rpmusicserver/web-interface
cp -r /tmp/rpmusicserver/web-interface/* /usr/local/bin/rpmusicserver/web-interface
echo " => program files installed." 

echo "Copy rc.local file:"
cp /tmp/rpmusicserver/files/rc.local /etc
chmod +x /etc/rc.local
echo " => file rc.local copied."     

echo "Copy revision.json file:"
mkdir -p /etc/rpms
cp /tmp/rpmusicserver/revision.json /etc/rpms
touch /etc/rpms/revision.json  # For retrieving last update timestamp
echo " => file revision.json copied." 

echo "Copy update-rpms file:"
cp /tmp/rpmusicserver/files/update-rpms /usr/local/bin
chmod +x /usr/local/bin/update-rpms
echo " => file update-rpms copied." 

# Execute /etc/rc.local for preloading docker containers
echo "Start executing /etc/rc.local..."
/etc/rc.local
echo "Done executing /etc/rc.local."

echo "Change password of user 'pi'..."
sed -i -e 's/pam_unix.so/pam_unix.so minlen=1/g' /etc/pam.d/common-password
# Note that changing password in su-mode (which is different than sudo-mode)
# does NOT require to enter the old password
echo -e "rpms\nrpms" | passwd pi
echo "Done changing password of user 'pi'."

echo "Installation complete, system will be rebooted."
reboot now
