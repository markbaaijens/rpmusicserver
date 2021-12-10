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
apt-get install docker.io python3-pip tree jq bwm-ng -y  # Generic
apt-get install vorbis-tools lame flac python3-mutagen python3-pil -y  # Transcoder
echo " => done installing packages."

echo "Setting timezone to Europe/Amsterdam..."
rm -rf /etc/localtime
ln -s /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime
echo " => done setting timezone."

echo "Creating mountpoint for usbdata-disk:"
if [ ! -d /media/usbdata ]; then
    mkdir /media/usbdata
    chmod 777 /media/usbdata -R
    echo " => mountpoint for usbdata created."    
else
    echo " => mountpoint for usbdata is already present."    
fi

echo "Creating mountpoint for usbackup-disk:"
if [ ! -d /media/usbackup ]; then
    mkdir /media/usbackup
    chmod 777 /media/usbackup -R
    echo " => mountpoint for usbackup created."    
else
    echo " => mountpoint for usbackup is already present."    
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

echo "Creating directories."
mkdir /media/usbdata/rpms/logs -p
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
if [ ! -d /media/usbdata/rpms/config/docker/lms ]; then
    mkdir -p /media/usbdata/rpms/config/docker/lms
    cp -r /tmp/rpmusicserver/files/config/lms/* /media/usbdata/rpms/config/docker/lms
    echo " => LMS config files copied."    
else
    echo " => LMS config folder is already present, no config files copied."    
fi

echo "Install (python) pip-packages:"
# Note that b/c this script is executed under sudo, pip3 packages are system-wide installed
pip3 install -r /tmp/rpmusicserver/web-interface/requirements.txt 
echo " => pip-packages installed." 

echo "Install program files for API:"
mkdir -p /usr/local/bin/rpmusicserver/web-interface
cp -r /tmp/rpmusicserver/web-interface/* /usr/local/bin/rpmusicserver/web-interface
echo " => program files installed." 

echo "Copy rc.local file:"
cp /tmp/rpmusicserver/files/etc/rc.local /etc
chmod +x /etc/rc.local
echo " => file rc.local copied."   

echo "Copy logrotate.conf file:"
cp /tmp/rpmusicserver/files/etc/logrotate.conf /etc
echo " => file logrotate.conf copied." 

echo "Copy revision.json file:"
mkdir -p /etc/rpms
cp /tmp/rpmusicserver/revision.json /etc/rpms
touch /etc/rpms/revision.json  # For retrieving last update timestamp
echo " => file revision.json copied." 

echo "Copy update-rpms file:"
cp /tmp/rpmusicserver/files/usr/local/bin/update-rpms /usr/local/bin
chmod +x /usr/local/bin/update-rpms
echo " => file update-rpms copied." 

echo "Installing transcoder..."
rm -rf /tmp/transcoder*
wget https://github.com/markbaaijens/transcoder/archive/refs/tags/v1.0.zip -nv -O /tmp/transcoder.zip
unzip -o -q -d /tmp -o /tmp/transcoder.zip
mv /tmp/transcoder-1.0 /tmp/transcoder
mkdir -p /usr/local/bin/transcoder
cp /tmp/transcoder/transcoder.py /usr/local/bin/transcoder/transcoder.py
chmod +x /usr/local/bin/transcoder/transcoder.py
if [ ! -f /media/usbdata/rpms/config/transcoder-settings.json ]; then
    cp /tmp/transcoder/transcoder-settings.json /media/usbdata/rpms/config/transcoder-settings.json
fi 
cp /tmp/rpmusicserver/files/usr/local/bin/transcode /usr/local/bin
chmod +x /usr/local/bin/transcode
echo " => transcoder installed"

echo "Adding line for transcoder to /etc/crontab:"
if [ ! "$(grep "transcode" /etc/crontab)" ]; then
    /bin/sh -c 'echo "20 * * * * root transcode" >> /etc/crontab'
    echo " => line added."    
else
    echo " => line is already present."    
fi

# Execute /etc/rc.local for preloading docker containers
echo "Start executing /etc/rc.local..."
/etc/rc.local
echo " => done executing /etc/rc.local."

echo "Change password of user 'pi'..."
sed -i -e 's/pam_unix.so/pam_unix.so minlen=1/g' /etc/pam.d/common-password
# Note that changing password in su-mode (which is different than sudo-mode)
# does NOT require to enter the old password
echo -e "rpms\nrpms" | passwd pi
echo " => done changing password of user 'pi'."

echo "Kill all docker-containers for faster rebooting"
if [ "$(docker ps -f name=lms -q)" ]; then
    docker kill lms
fi
if [ "$(docker ps -f name=transmission -q)" ]; then
    docker kill transmission
fi
if [ "$(docker ps -f name=samba -q)" ]; then
    docker kill samba
fi
echo " => done killing docker containers"

echo "Installation complete, system will be rebooted."
reboot now
