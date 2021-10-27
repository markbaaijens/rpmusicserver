#!/bin/bash

if [ -z "$(whoami | grep root)" ]
then
    echo "Not running as root."
    echo "Script ended with failure."
    exit
fi

setup_environment() {
    echo "Setup environment."    
    export LC_ALL=C  # Console output = English
}

cleanup_environment() {
    echo "Cleaning up environment."
    unset LC_ALL  # Reset console output to default language
}

setup_environment

readarray -t disks < <(lsblk -b -e7 -o name,type | grep disk | awk '{print $1}')
sd_disks=()
for disk in "${disks[@]}"; do
    model=$(parted /dev/$disk print | grep Model)
   if [[ ! $model == *"nvme"* ]]
   then
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
    model=$(parted /dev/$disk print | grep Model | cut -d " " -f2- )
    size=$(parted /dev/$disk print | grep "Disk /dev/" | awk '{print $3}')
  	echo "$counter: $model/$disk ($size) $([ $counter == 0 ] && echo "[default]")"
	counter=$(($counter + 1))
done
echo "q: quit"

read -p "Select a disk by number or press [Enter] to choose the first one " disk_choice

if [  "$disk_choice" == "q" ] || [ "${sd_disks[disk_choice]}" == "" ]; then
    echo "No disk selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi

chosen_disk=${sd_disks[disk_choice]}
echo "You have chosen: ${disks[$chosen_disk]}"

# todo variable not working
sdcard=$chosen_disk

# get the label and its partitions from the sd-card
sdlabel=$(echo "$sdcard" | head -n 1)
partitions=$(echo "$sdcard" | grep -vw "$sdlabel" | grep -oE "($sdlabel)p$number_pattern")

# Ask user confirmation before formatting (see burn-image.sh)
read -r -p "Do you want continue formatting $sdlabel? [yes/NO] " start_install
if [ "$start_install" != "yes" ]  
then
    cleanup_environment
    echo "Script ended by user."
    exit
fi

# Wipe USB-disk
	# Wipe disk
#	lsblk | grep disk
#	sudo umount /dev/sda1
#	sudo wipefs -a /dev/sda
	# Or: sudo dd if=/dev/zero of=/dev/sda bs=512 count=1 conv=notrunc
#	sudo hdparm -z /dev/sda  # Alternative: sudo partprobe /dev/sda

# Format with ext4
# Attach label, fixed name = usbdisk
	# Create new partition table
	# Scripting fdisk  to create partition:
	#   n = new partition
	#   p = primary
	#   1 = Enter = nuber
	#   First sector: enter
	#   Last sector: enter
	#   w = write
#	echo -e "o\nn\np\n1\n\n\nw" | sudo fdisk /dev/sda
#	sudo hdparm -z /dev/sda
#	lsblk  # Check
	
	# Format partition as ext4
#	sudo mkfs.ext4 -L 'usbdata' /dev/sda1
#	sudo hdparm -z /dev/sda
	# Check label:  sudo e2label /dev/sdXY

cleanup_environment
	