#!/bin/bash

# TODO
# - DISK BACKUP-RPMS
# - install nmap
# - install sshpass

disk_label="BACKUP-RPMS"
if [ ! -d /run/media/$USER/$disk_label ]; then 
    echo "Connect your backup-disk named $disk_label, exit"
    exit
fi
echo "Disk named as $disk_label found"

echo "Discovering RPMS-servers..."

readarray -t web_servers < <(nmap $(echo "$(hostname -I | cut -d"." -f1-3).1")/24 -p 80 --open -oG /tmp/nmap.txt > /dev/null && cat /tmp/nmap.txt | grep Ports | awk '{print $2}')
rpms_servers=()
for server in "${web_servers[@]}"; do
    if [[ $(nmap $server -sV --version-intensity 0 -p 80 | grep Werkzeug) ]]; then
        rpms_servers+=("$server")
    fi
done

if [[ ${#rpms_servers[@]} -eq 0 ]]; then
    echo "No servers found, exit"
    exit
fi

if [[ ${#rpms_servers[@]} -gt 1 ]]; then
    addresses=""
    for server in "${rpms_servers[@]}"; do
        addresses+="$server "
    done

    echo "Multiple servers found at $addresses"
    echo "Make sure one and only one server is active, exit"    
    
    exit
fi

server=${rpms_servers[0]}
echo "Server found at $server"

echo "Backup is in progress..."

ssh-keygen -R $server > /dev/null
ssh-keyscan -H $server >> ~/.ssh/known_hosts

sshpass -p rpms rsync --progress --delete -rtv --max-size=4GB --modify-window=2 --exclude Downloads \
	pi@$server:/media/usbdata/user/* \
	/run/media/$USER/$disk_label/user
	
sync
echo "Backup is complete, you can safely remove the disk..."

