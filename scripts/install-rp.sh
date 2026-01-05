#!/bin/bash

log () {
    # Normally rpms-logs reside in /media/usbdata/rpms/logs. But b/c this location 
    # might be unavailable during install b/c mounts are not in place, we opt 
    # for a location which is always accessible, /var/log.
    log_dir="/var/log"
    echo "$1"
    echo "$(date "+%Y-%m-%d") $(date +%H:%M:%S) $1" >> $log_dir/update-details.log
}

install_bin_file () {
    log "Copy $1 to /usr/local/bin"
    cp /tmp/rpmusicserver/files/usr/local/bin/$1 /usr/local/bin
    chmod +x /usr/local/bin/$1
}

if [ -z "$(whoami | grep root)" ]; then
    echo "Not running as root."
    exit
fi

rm -f /var/log/update-details.log

log "Updating apt package-source"
apt-get update

log "Installing apt-packages"
apt-get install docker.io python3-pip tree jq bwm-ng nmap zip -y   # Generic
apt-get install vorbis-tools lame flac python3-mutagen python3-pil -y  # Transcoder
apt-get install samba -y
apt-get install dnsutils -y
apt-get install ffmpeg -y
apt-get install id3v2 -y

log "Setting timezone to Europe/Amsterdam"
rm -rf /etc/localtime
ln -s /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime

if [ ! -d /media/usbdata ]; then
    log "Creating mountpoint for usbdata-disk"
    mkdir /media/usbdata
    chmod 777 /media/usbdata -R
fi

if [ ! -d /media/usbbackup ]; then
    log "Creating mountpoint for usbbackup-disk"
    mkdir /media/usbbackup
    chmod 777 /media/usbbackup -R
fi

# By always delete existing lines in fstab, we can easily implement
# a different strategy later, if needed

log "Adding line for usbdata-disk to /etc/fstab"
sed -i '/usbdata/d' /etc/fstab  
# auto,nofail: server starts even when harddisk is not present
/bin/sh -c 'echo "LABEL=usbdata /media/usbdata ext4 auto,nofail 0 0" >> /etc/fstab'

log "Adding line for usbbackup-disk to /etc/fstab"
sed -i '/usbbackup/d' /etc/fstab
# auto,nofail: server starts even when harddisk is not present; x-systemd.automount: automounting usbbackup
/bin/sh -c 'echo "LABEL=usbbackup /media/usbbackup ext4 auto,nofail,x-systemd.automount 0 0" >> /etc/fstab'

mount -a

log "Creating directories on /media/usbdata"
mkdir /media/usbdata/rpms/logs -p

mkdir /media/usbdata/user/public -p
chmod 777 /media/usbdata/user/public

mkdir /media/usbdata/user/music -p
chmod 777 /media/usbdata/user/music

if [ ! -d /media/usbdata/rpms/config/docker/lms ]; then
    log "Copy LMS config files"
    mkdir -p /media/usbdata/rpms/config/docker/lms
    cp -r /tmp/rpmusicserver/files/config/lms/* /media/usbdata/rpms/config/docker/lms
fi

log "Install (python) pip-packages"
# Note that b/c this script is executed under sudo, pip3 packages are system-wide installed
pip3 install -r /tmp/rpmusicserver/web-interface/requirements.txt 

log "Copy rc.local to /etc"
cp /tmp/rpmusicserver/files/etc/rc.local /etc
chmod +x /etc/rc.local

log "Copy logrotate.conf to /etc"
cp /tmp/rpmusicserver/files/etc/logrotate.conf /etc

log "Copy revision.json to /etc/rpms"
mkdir -p /etc/rpms
cp /tmp/rpmusicserver/revision.json /etc/rpms
touch /etc/rpms/revision.json  # For retrieving last update timestamp

log "Installing transcoder"
rm -rf /tmp/transcoder*
wget https://github.com/markbaaijens/transcoder/archive/refs/tags/v1.2.zip -nv -O /tmp/transcoder.zip
unzip -o -q -d /tmp -o /tmp/transcoder.zip
mv /tmp/transcoder-1.2 /tmp/transcoder
mkdir -p /usr/local/bin/transcoder
rm -rf /usr/local/bin/transcoder/*
cp /tmp/transcoder/transcoder.py /usr/local/bin/transcoder/transcoder.py
chmod +x /usr/local/bin/transcoder/transcoder.py

find /usr/local/bin/ -maxdepth 1 -type f -delete  # rm tries to remove subfolders also, so we use find
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
install_bin_file flac-health-check
install_bin_file flac-health-report
install_bin_file flac-health-repair
install_bin_file apt-upgrade-unattended

log "Removing obsolete line for setting rights in /etc/crontab created by a previous version of RPMS"
sed -i '/chmod 777/d' /etc/crontab

# By always delete existing lines in crontab, we can easily implement
# a different strategy later, if needed
log "Adding line for transcode in /etc/crontab"
sed -i '/transcode/d' /etc/crontab
/bin/sh -c 'echo "20  * * * * root transcode" >> /etc/crontab'

log "Adding line for apt-upgrade in /etc/crontab"
sed -i '/apt-get upgrade/d' /etc/crontab  # Remove commands from previous version
sed -i '/apt-upgrade-unattended/d' /etc/crontab
/bin/sh -c 'echo "00 02 * * * root apt-upgrade-unattended" >> /etc/crontab'

log "Adding line for update-docker in /etc/crontab"
sed -i '/update-docker/d' /etc/crontab
/bin/sh -c 'echo "00 03 * * * root update-docker" >> /etc/crontab'

log "Adding line for export-collection in /etc/crontab"
sed -i '/export-collection/d' /etc/crontab
/bin/sh -c 'echo "10 03 * * * root export-collection" >> /etc/crontab'

log "Adding line for backup rpms-system in /etc/crontab"
sed -i '/backup-rpms-system/d' /etc/crontab
/bin/sh -c 'echo "20 03 * * * root backup-rpms-system" >> /etc/crontab'

log "Adding line for backup-server in /etc/crontab"
sed -i '/backup-server/d' /etc/crontab
/bin/sh -c 'echo "30 03 * * * root backup-server" >> /etc/crontab'

log "Adding line for flac-health-check in /etc/crontab"
sed -i '/flac-health-check/d' /etc/crontab
/bin/sh -c 'echo "00 04 * * * root flac-health-check" >> /etc/crontab'

log "Change password of user 'pi'"
sed -i -e 's/pam_unix.so/pam_unix.so minlen=1/g' /etc/pam.d/common-password
# Note that changing password in su-mode (which is different than sudo-mode)
# does NOT require to enter the old password
echo -e "rpms\nrpms" | passwd pi

log "Change swappiness to 1"
if ([ $(grep -c 'vm.swappiness=1' /etc/sysctl.conf) -eq 0 ]); then
    /bin/sh -c 'echo "vm.swappiness=1" >> /etc/sysctl.conf'
fi

log "Limit size of /var/log/journal"
sed -i '/SystemMaxUse/d' /etc/systemd/journald.conf
/bin/sh -c 'echo "SystemMaxUse=50M" >> /etc/systemd/journald.conf'

if [ ! -f /media/usbdata/rpms/config/translations.json ]; then
    log "Generate translations.json"

    lang_choice="e"
    if [ -f /etc/lang-choice.txt ]; then
        lang_choice="$(cat /etc/lang-choice.txt)"
        log "- language from /etc/lang-choice.txt = '$lang_choice'"
    else
        log "- file /etc/lang-choice.txt not found, resorting to default = 'e'"
    fi

    # 'e' = default and also fail-safe
    public_share_name="Public"
    music_share_name="Music"
    backup_share_name="Backup"

    if [ "$lang_choice" == "d" ]; then
        public_share_name="Publiek"
        music_share_name="Muziek"
        backup_share_name="Backup"
    fi

    if [ "$lang_choice" == "g" ]; then
        public_share_name="Öffentlich"
        music_share_name="Muzik"
        backup_share_name="Sicherung"
    fi

    if [ "$lang_choice" == "f" ]; then
        public_share_name="Public"
        music_share_name="Musique"
        backup_share_name="Sauvegarde"
    fi

    jq --null-input \
    --arg public_share_name "$public_share_name" \
    --arg music_share_name "$music_share_name" \
    --arg backup_share_name "$backup_share_name" '{"PublicShareName": $public_share_name, "MusicShareName": $music_share_name, "BackupShareName": $backup_share_name }' > /media/usbdata/rpms/config/translations.json
fi
rm /etc/lang-choice.txt -rf

# Generating smb.conf must be done *after* translations have been set b/c share-names are translated
log "Generate samba-configuration"
generate-samba-conf

log "Start docker for preloading containers"
start-docker

log "Install program files for web-interface"
mkdir -p /usr/local/bin/rpmusicserver/web-interface
rm -rf /usr/local/bin/rpmusicserver/web-interface/*
cp -r /tmp/rpmusicserver/web-interface/* /usr/local/bin/rpmusicserver/web-interface

log "Installation complete, system will be rebooted"
reboot-server
