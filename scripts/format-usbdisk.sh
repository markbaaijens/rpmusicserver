#!/bin/bash

if [ -z "$(whoami | grep root)" ]; then
    echo "Not running as root."
    exit
fi

setup_environment() {
    export LC_ALL=C  # Console output = English
}

cleanup_environment() {
    unset LC_ALL  # Reset console output to default language
}

setup_environment

readarray -t disks < <(lsblk -b -e7 -o name,type | grep disk | awk '{print $1}')
sd_disks=()
for disk in "${disks[@]}"; do
    model=$(parted /dev/$disk print | grep Model)
    if [[ ! $model == *"nvme"* ]]; then
        sd_disks+=("$disk")
    fi
done

if [ "${sd_disks[0]}" == "" ]; then
    echo "No disk available."
    cleanup_environment	
    echo "Script ended with failure." 
    exit
fi

echo "Available disk(s):"
counter=0
for disk in "${sd_disks[@]}"; do
    model=$(parted /dev/$disk print | grep Model | cut -d " " -f3- )
    size=$(parted /dev/$disk print | grep "Disk /dev/" | awk '{print $3}')
  	echo "$counter: $model/$disk ($size)"
    counter=$(($counter + 1))
done
echo "Q: quit"

read -p "Select a disk: " disk_choice

if [ "${disk_choice,,}" == "q" ]; then
    cleanup_environment    
    echo "Script ended by user."
    exit
fi

if [ "$disk_choice" == "" ] || [ "${sd_disks[disk_choice]}" == "" ]; then
    echo "No disk selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi

chosen_disk=${sd_disks[disk_choice]}
echo "You have chosen: $chosen_disk"

echo "Format as:"
echo "d: DATA-disk (ext4, label = usbdata)"
echo "b: BACKUP-disk (ext4, label = usbbackup)"
echo "Q: quit"

read -p "Select a format-type: " type_choice

if [ "$type_choice" == "" ]; then
    type_choice=0
fi

if [ "${type_choice,,}" == "q" ]; then
    cleanup_environment    
    echo "Script ended by user."
    exit
fi

if [ ${type_choice,,} != "d" ] && [ ${type_choice,,} != "b" ]; then
    echo "No type selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi
echo "You have chosen: $type_choice $([ $type_choice == 1 ] && echo "=> usbdata" || echo "=> usbbackup")"

read -r -p "Do you want to continue formatting '$chosen_disk' as $([ $type_choice == 1 ] && echo "'usbdata'" || echo "'usbbackup'")? [yes/NO] " start_install
if [ "$start_install" != "yes" ]; then
    cleanup_environment
    echo "Script ended by user."
    exit
fi

echo "Starting unmounting /dev/$chosen_disk partitions..."
partitions=$(lsblk -l -n -p -e7 /dev/$chosen_disk | grep part | awk '{print $1}')
for partition in $partitions; do
    sleep 3	
	echo "Unmouting $partition"
    umount -f "$partition"
	if [ -n "$(df | grep /dev/$partition)" ]; then
        echo "Failed to umount /dev/$partition."
        cleanup_environment
        echo "Script ended with failure."
        exit
    fi    
    echo "Partition $partition successfully unmounted."
done
hdparm -z /dev/$chosen_disk
echo " => done unmounting /dev/$chosen_disk partitions."

echo "Start wiping $chosen_disk..."
wipefs -a "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk
echo " => done wiping $chosen_disk."

# Scripting fdisk to create partition:
#   n = new partition
#   p = primary
#   1 = Enter = nuber
#   First sector: enter
#   Last sector: enter
#   w = write
echo "Start creating partition on $chosen_disk..."
echo -e "o\nn\np\n1\n\n\nw" | fdisk /dev/$chosen_disk
hdparm -z /dev/$chosen_disk
echo " => done creating partition on $chosen_disk."

disk_label=""
if [ ${type_choice,,} == "d" ]; then
    disk_label="usbdata"
else
    disk_label="usbbackup"
fi    

echo "Start formatting partition on $chosen_disk as '$disk_label'..."	
mkfs.ext4 -L "$disk_label" "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk
echo " => done formatting partition on $chosen_disk."		

cleanup_environment
echo "Script ended successfully."

exit
