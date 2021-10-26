#!/bin/bash
export LC_ALL=C

if [ -z "$(whoami | grep root)" ]
then
  echo "Not running as root."
  echo "Script ended."
  exit
fi

readarray -t disks < <(lsblk -b -e7 -o name,type | grep disk | awk '{print $1}')
sd_disks=()
for disk in "${disks[@]}"; do
    model=$(parted /dev/$disk print | grep Model)
    if [[ $model == *"sd/mmc"* ]]; then
        sd_disks+=("$disk")
    fi
done

if [ "${sd_disks[0]}" == "" ]; then
    echo "No disk available."
    echo "Script ended." 
    exit
fi

echo "Available disk(s):"
counter=0
for disk in "${sd_disks[@]}"; do
    model=$(parted /dev/$disk print | grep Model | cut -d " " -f2- )
    size=$(parted /dev/$disk print | grep Disk | awk '{print $3}')
    echo "$counter: $model/$disk ($size)"
    counter=$(($counter + 1))
done

unset LC_ALL

read -p "Select a disk by number or press [Enter] to choose the first one " disk_choice

if [ "${sd_disks[disk_choice]}" == "" ]; then
    echo "No disk selected."
    echo "Script ended."    
    exit
fi

chosen_disk=${sd_disks[disk_choice]}
echo "You have chosen: $chosen_disk"

exit