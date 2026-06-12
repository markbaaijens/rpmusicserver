#!/bin/bash

secs_to_human() {
    if [[ -z ${1} || ${1} -lt 60 ]] ;then
        min=0 ; secs="${1}"
    else
        time_mins=$(echo "scale=2; ${1}/60" | bc)
        min=$(echo ${time_mins} | cut -d'.' -f1)
        secs="0.$(echo ${time_mins} | cut -d'.' -f2)"
        secs=$(echo ${secs}*60|bc|awk '{print int($1+0.5)}')
    fi
    echo "Time Elapsed: ${min} minutes and ${secs} seconds"
}

if [[ ! $(apt -qq list nmap -o "Apt::Cmd::Disable-Script-Warning=true") ]]; then
    echo "Install nmap: sudo apt install nmap"
    exit
fi
if [[ ! $(apt -qq list sshpass -o "Apt::Cmd::Disable-Script-Warning=true") ]]; then
    echo "Install nmap: sudo apt install sshpass"
    exit
fi

disk_label="BACKUP-RPMS"
if [ ! -d /run/media/$USER/$disk_label ]; then 
    echo "Connect your backup-disk named $disk_label"
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
    echo "No servers found"
    exit
fi

if [[ ${#rpms_servers[@]} -gt 1 ]]; then
    addresses=""
    for server in "${rpms_servers[@]}"; do
        addresses+="$server "
    done

    echo "Multiple servers found at $addresses"
    echo "Make sure one and only one server is active"
    
    exit
fi

server=${rpms_servers[0]}
echo "Server found at $server"

echo "Backup is in progress..."

ssh-keygen -R $server > /dev/null
ssh-keyscan -H $server >> ~/.ssh/known_hosts

SECONDS=0
sshpass -p rpms rsync --progress --delete -rtv --max-size=4GB --modify-window=2 --exclude Downloads \
	pi@$server:/media/usbdata/user/* \
	/run/media/$USER/$disk_label/user
	
sync
secs_to_human $SECONDS

echo "Backup is complete, you can now safely remove the disk..."

