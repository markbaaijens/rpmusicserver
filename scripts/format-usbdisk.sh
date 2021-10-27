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
echo "Q: quit"

read -p "Select a disk by number or press [Enter] to choose the first one " disk_choice

if [  "$disk_choice" == "q" ] || [ "${sd_disks[disk_choice]}" == "" ]; then
    echo "No disk selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi

chosen_disk=${sd_disks[disk_choice]}
echo "You have chosen: $chosen_disk"

read -r -p "Do you want continue formatting $chosen_disk? [yes/NO] " start_install
if [ "$start_install" != "yes" ]  
then
    cleanup_environment
    echo "Script ended by user."
    exit
fi

echo "Starting unmounting /dev/$chosen_disk partitions..."
partitions=$(lsblk -l -n -p -e7 /dev/$chosen_disk | grep part | awk '{print $1}')
for partition in $partitions; do
	echo "Unmouting $partition"
    umount -f "$partition"
 	sleep 3	
    echo "Partition $partition successfully unmounted."
done
hdparm -z /dev/$chosen_disk
echo "Done unmounting /dev/$chosen_disk partitions."

echo "Start wiping $chosen_disk..."
wipefs -a "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk
echo "Done wiping $chosen_disk."

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
echo "Done creating partition on $chosen_disk."
	
echo "Start formatting partition on $chosen_disk..."	
mkfs.ext4 -L 'usbdata' "/dev/$chosen_disk"1
hdparm -z /dev/$chosen_disk
echo "Done formatting partition on $chosen_disk."		

cleanup_environment
echo "Script ended successfully."

exit
