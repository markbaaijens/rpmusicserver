#!/bin/bash

# TODO
# - command apt -qq list does not work (should have grep or something)

backup_time() {
    if [[ -z ${1} || ${1} -lt 60 ]] ;then
        min=0 ; secs="${1}"
    else
        time_mins=$(echo "scale=2; ${1}/60" | bc)
        min=$(echo ${time_mins} | cut -d'.' -f1)
        secs="0.$(echo ${time_mins} | cut -d'.' -f2)"
        secs=$(echo ${secs}*60|bc|awk '{print int($1+0.5)}')
    fi
    echo "Backup completed in ${min} minute(s) and ${secs} second(s)"
}

get_hostname() {
    hostname="$(nbtscan $1 | tail -1 | awk '{print $2}')"
}

check_package() {
    echo "Check package $1"
    if [[ ! $(apt -qq list $1 -o "Apt::Cmd::Disable-Script-Warning=true") ]]; then
        echo "Install $1: sudo apt install $1"
        exit
    fi    
}

server_param=$1

check_package nmap
check_package sshpass
check_package nbtscan
exit

disk_label="BACKUP-RPMS"
if [ ! -d /run/media/$USER/$disk_label ]; then 
    echo "Connect a backup-disk named $disk_label to this machine"
    exit
fi
echo "Disk named $disk_label found"

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

if [[ ${#rpms_servers[@]} -gt 0 ]]; then
    addresses=""
    addresses_extra=""
    for server in "${rpms_servers[@]}"; do
        get_hostname $server
        addresses+="$server "
        addresses_extra+="$server ($hostname) "
    done
fi
echo "Server(s) found: $addresses_extra"

if [[ "$server_param" = "" ]]; then
    if [[ ${#rpms_servers[@]} -gt 1 ]]; then
        echo "Multiple servers found: make sure only one server is active or specify server as parameter"
        exit
    else
        server=${rpms_servers[0]}
    fi
else
    if [[ ! "$addresses" =~ "$server_param" ]]; then
        echo "Given server $server_param is not valid"
        exit
    else
        server=$1
    fi
fi

get_hostname $server
echo "Selected server: $server ($hostname)"

ssh-keygen -R $server > /dev/null
ssh-keyscan -H $server >> ~/.ssh/known_hosts

if [ ! -d /run/media/$USER/$disk_label/user ]; then 
    mkdir /run/media/$USER/$disk_label/user
fi

echo "Backup is in progress..."

SECONDS=0
sshpass -p rpms rsync --progress --delete -rtv --max-size=4GB --modify-window=2 \
	pi@$server:/media/usbdata/user/* \
	/run/media/$USER/$disk_label/user
	
sync

echo ""
backup_time $SECONDS
echo "You can now safely remove the disk..."

