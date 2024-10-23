#!/bin/bash

install_bin_file () {
    echo "Copy $1 file"
    cp /tmp/rpmusicserver/files/usr/local/bin/$1 /usr/local/bin
    chmod +x /usr/local/bin/$1
    echo "... file $1 copied." 
}

if [ -z "$(whoami | grep root)" ]; then
    echo "Not running as root."
    echo "Script ended with failure."
    exit
fi

echo "Installing packages..."
apt-get update
apt-get install docker.io python3-pip tree jq bwm-ng nmap zip -y   # Generic
apt-get install vorbis-tools lame flac python3-mutagen python3-pil -y  # Transcoder
apt-get install samba -y
echo "... done installing packages."

echo "Setting timezone to Europe/Amsterdam..."
rm -rf /etc/localtime
ln -s /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime
echo "... done setting timezone."

echo "Creating mountpoint for usbdata-disk"
if [ ! -d /media/usbdata ]; then
    mkdir /media/usbdata
    chmod 777 /media/usbdata -R
    echo "... mountpoint for usbdata created."    
else
    echo "... mountpoint for usbdata is already present."    
fi

echo "Creating mountpoint for usbbackup-disk"
if [ ! -d /media/usbbackup ]; then
    mkdir /media/usbbackup
    chmod 777 /media/usbbackup -R
    echo "... mountpoint for usbbackup created."    
else
    echo "... mountpoint for usbbackup is already present."
fi

echo "Cleanup /usr/local/bin"
rm -rf /usr/local/bin/*
echo "... cleaned up."

echo "Adding line for usbdata-disk to /etc/fstab"
if [ ! "$(grep "LABEL=usbdata" /etc/fstab)" ]; then
    # auto,nofail: server starts even when harddisk is not present
    /bin/sh -c 'echo "LABEL=usbdata /media/usbdata ext4 auto,nofail 0 0" >> /etc/fstab'
    echo "... line added."
else
    echo "... line is already present."    
fi

echo "Adding line for usbbackup-disk to /etc/fstab"
if [ ! "$(grep "LABEL=usbbackup" /etc/fstab)" ]; then
    # auto,nofail: server starts even when harddisk is not present
    /bin/sh -c 'echo "LABEL=usbbackup /media/usbbackup ext4 auto,nofail 0 0" >> /etc/fstab'
    echo "... line added."
else
    echo "... line is already present."    
fi    

mount -a

echo "Creating directories."
mkdir /media/usbdata/rpms/logs -p

mkdir /media/usbdata/user/public -p
chmod 777 /media/usbdata/user/public

mkdir /media/usbdata/user/public/Downloads -p
chmod 777 /media/usbdata/user/public/Downloads

mkdir /media/usbdata/user/music -p
chmod 777 /media/usbdata/user/music

echo "Copy LMS config files"
if [ ! -d /media/usbdata/rpms/config/docker/lms ]; then
    mkdir -p /media/usbdata/rpms/config/docker/lms
    cp -r /tmp/rpmusicserver/files/config/lms/* /media/usbdata/rpms/config/docker/lms
    echo "... LMS config files copied."    
else
    echo "... LMS config folder is already present, no config files copied."    
fi

echo "Install (python) pip-packages"
# Note that b/c this script is executed under sudo, pip3 packages are system-wide installed
pip3 install -r /tmp/rpmusicserver/web-interface/requirements.txt 
echo "... pip-packages installed." 

echo "Install program files for web-interface"
mkdir -p /usr/local/bin/rpmusicserver/web-interface
cp -r /tmp/rpmusicserver/web-interface/* /usr/local/bin/rpmusicserver/web-interface
echo "... program files for web-interface installed." 

echo "Copy rc.local file"
cp /tmp/rpmusicserver/files/etc/rc.local /etc
chmod +x /etc/rc.local
echo "... file rc.local copied."   

echo "Copy logrotate.conf file"
cp /tmp/rpmusicserver/files/etc/logrotate.conf /etc
echo "... file logrotate.conf copied." 

echo "Copy revision.json file"
mkdir -p /etc/rpms
cp /tmp/rpmusicserver/revision.json /etc/rpms
touch /etc/rpms/revision.json  # For retrieving last update timestamp
echo "... file revision.json copied." 

echo "Installing transcoder..."
rm -rf /tmp/transcoder*
wget https://github.com/markbaaijens/transcoder/archive/refs/tags/v1.2.zip -nv -O /tmp/transcoder.zip
unzip -o -q -d /tmp -o /tmp/transcoder.zip
mv /tmp/transcoder-1.2 /tmp/transcoder
mkdir -p /usr/local/bin/transcoder
cp /tmp/transcoder/transcoder.py /usr/local/bin/transcoder/transcoder.py
chmod +x /usr/local/bin/transcoder/transcoder.py

if [ ! -f /media/usbdata/rpms/config/transcoder-settings.json ]; then
    cp /tmp/rpmusicserver/files/config/transcoder/transcoder-settings.json /media/usbdata/rpms/config/transcoder-settings.json
fi 
echo "... transcoder installed."

install_bin_file update-rpms
install_bin_file backup-server
install_bin_file backup-rpms-system
install_bin_file transcode
install_bin_file start-docker
install_bin_file kill-docker
install_bin_file update-docker
install_bin_file halt-server
install_bin_file reboot-server
install_bin_file export-collection
install_bin_file start-web
install_bin_file generate-samba-conf

# By always delete existing lines in crontab, we can easily implement
# a different crontab-strategy later, if needed
echo "Adding line to transcode in /etc/crontab..."
sed -i '/transcode/d' /etc/crontab
/bin/sh -c 'echo "20  * * * * root transcode" >> /etc/crontab'
echo "... line added."    

echo "Adding line to apt-upgrade in /etc/crontab..."
sed -i '/apt-get upgrade/d' /etc/crontab
/bin/sh -c 'echo "00 02 * * * root apt-get upgrade -y && apt-get clean -y && apt-get autoremove -y && apt-get autoclean -y" >> /etc/crontab'
echo "... line added."    

echo "Removing line to set rights in /etc/crontab..."
sed -i '/chmod 777/d' /etc/crontab
echo "... line removed."    

echo "Adding line to update-docker in /etc/crontab..."
sed -i '/update-docker/d' /etc/crontab
/bin/sh -c 'echo "00 03 * * * root update-docker" >> /etc/crontab'
echo "... line added."    

echo "Adding line to export-collection in /etc/crontab..."
sed -i '/export-collection/d' /etc/crontab
/bin/sh -c 'echo "10 03 * * * root export-collection" >> /etc/crontab'
echo "... line added."    

echo "Adding line to backup rpms-system in /etc/crontab..."
sed -i '/backup-rpms-system/d' /etc/crontab
/bin/sh -c 'echo "20 03 * * * root backup-rpms-system" >> /etc/crontab'
echo "... line added."    

echo "Change password of user 'pi'..."
sed -i -e 's/pam_unix.so/pam_unix.so minlen=1/g' /etc/pam.d/common-password
# Note that changing password in su-mode (which is different than sudo-mode)
# does NOT require to enter the old password
echo -e "rpms\nrpms" | passwd pi
echo "... done changing password of user 'pi'."

echo "Change swappiness to 1"
if ([ $(grep -c 'vm.swappiness=1' /etc/sysctl.conf) -eq 0 ]); then
    /bin/sh -c 'echo "vm.swappiness=1" >> /etc/sysctl.conf'
fi

echo "Limit size of /var/log/journal"
sed -i '/SystemMaxUse/d' /etc/systemd/journald.conf
/bin/sh -c 'echo "SystemMaxUse=50M" >> /etc/systemd/journald.conf'

echo "Generate translations.json"
if [ -f /etc/lang-choice.txt ]; then
    if [ ! -f /media/usbdata/rpms/config/translations.json ]; then
        echo "- generating translations.json"
        public_share_name="Public"
        music_share_name="Music"
        backup_share_name="Backup"

        if [ "$(grep "d" /etc/lang-choice.txt)" ]; then
            public_share_name="Publiek"
            music_share_name="Muziek"
            backup_share_name="Backup"
        fi

        if [ "$(grep "g" /etc/lang-choice.txt)" ]; then
            public_share_name="Öffentlich"
            music_share_name="Muzik"
            backup_share_name="Sicherung"
        fi

        if [ "$(grep "f" /etc/lang-choice.txt)" ]; then
            public_share_name="Public"
            music_share_name="Musique"
            backup_share_name="Sauvegarde"
        fi

        jq --null-input \
        --arg public_share_name "$public_share_name" \
        --arg music_share_name "$music_share_name" \
        --arg backup_share_name "$backup_share_name" '{"PublicShareName": $public_share_name, "MusicShareName": $music_share_name, "BackupShareName": $backup_share_name }' > /media/usbdata/rpms/config/translations.json

        rm /etc/lang-choice.txt
    else
        echo "- translations.json already present"
    fi
else
    echo "- /etc/lang-choice.txt not found"    
fi
echo "... done generating translations.json."

# Generating smb.conf must be done *after* translations have been set b/c share-names are translated
echo "Generate samba-configuration..."
generate-samba-conf
echo "... done generating samba-configuration."

echo "Start docker for preloading containers"
start-docker
echo "... done starting docker-containers."

echo "Start web-services"
start-web
echo "... done starting web-services."

echo "Installation complete."

