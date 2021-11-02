#!/bin/bash
#
# This script will burn the Raspbian OS Lite Image from the raspberrypi.org server and burn the image to a SD-card.
#

if [ -z "$(whoami | grep root)" ]; then
    echo "Not running as root."
    echo "Script ended with failure."
    exit
fi

working_dir=/tmp/raspbian
image=https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip
archive=raspbian-os-lite.zip
mnt_boot=/mnt/boot
number_pattern="[0-9]+"

setup_environment() {
    echo "Setup environment"    
    if [ ! -d $working_dir ]; then 
        mkdir $working_dir
    fi
    export LC_ALL=C  # Console output = English
}

cleanup_environment() {
    echo "Cleaning up environment"
    unset LC_ALL  # Reset console output to default language
}

setup_environment

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
    cleanup_environment
    echo "Script ended with failure." 
    exit
fi

echo "Available disk(s):"
counter=0
for disk in "${sd_disks[@]}"; do
    model=$(parted /dev/$disk print | grep "Model" | cut -d " " -f2- )
    size=$(parted /dev/$disk print | grep "Disk /dev/" | awk '{print $3}')
    echo "$counter: $model /dev/$disk ($size) $([ $counter == 0 ] && echo "[default]")"
    counter=$(($counter + 1))
done
echo "Q: quit"

read -p "Select a disk by number or press [Enter] to choose the first one " disk_choice

if [ "${disk_choice,,}" == "q" ] || [ "${sd_disks[disk_choice]}" == "" ]; then
    echo "No disk selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi

chosen_disk=${sd_disks[disk_choice]}
echo "You have chosen: $chosen_disk"

read -r -p "Do you want to start installation on $chosen_disk? [yes/NO] " start_install
if [ "$start_install" != "yes" ]; then
    cleanup_environment
    echo "Script ended by user."
    exit
fi

echo "Unmounting /dev/$chosen_disk partitions..."
partitions=$(lsblk -l -n -p -e7 /dev/$chosen_disk | grep part | awk '{print $1}')
for partition in $partitions; do
    # todo testen
    sleep 3
    umount -f "$partition"
	if [ -n "$(df | grep $partition)" ]; then
        echo "Failed to umount $partition."
        cleanup_environment
        echo "Script ended with failure."
        exit
    fi
   	echo "Partition /dev/$partition successfully unmounted."
done
hdparm -z /dev/$chosen_disk
echo "Done unmounting /dev/$chosen_disk partitions"

if [ ! $(dpkg --list | grep wget | awk '{print $1}' | grep ii) ]; then 
    apt install wget -y
fi
echo "Downloading image..."
wget -c --show-progress -P $working_dir -O $working_dir/$archive $image
echo "Download complete"

if [ "$(sha256sum $working_dir/$archive | cut -d' ' -f1)" != "c5dad159a2775c687e9281b1a0e586f7471690ae28f2f2282c90e7d59f64273c" ]; then
    echo "Checksum of the Raspbian image failed."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi

echo "Extracting $working_dir/$archive..."
unzip -o $working_dir/$archive -d $working_dir
echo "Done extracting archive"
extracted_img=$(ls -t $working_dir/*.img | head -n 1)
if [ -z $extracted_img ]; then
    echo "No image found in $working_dir."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi
echo "Done extracting $working_dir/$archive"

echo "Start wiping $chosen_disk..."
wipefs -a "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk
echo "Done wiping $chosen_disk."

if [ ! $(dpkg --list | grep gddrescue | awk '{print $1}' | grep ii) ]; then 
    apt install gddrescue -y
fi
echo "Start burning $extracted_img to $chosen_disk..."
ddrescue -D --force $extracted_img "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk
echo "Done burning $chosen_disk."

if [ ! -d $mnt_boot ]; then 
    mkdir $mnt_boot
fi
sleep 3

if [ ! -d /dev/disk/by-label ]; then
	echo "/dev/disk/by-label doesn't exist"
    cleanup_environment
    echo "Script ended with failure."
    exit
fi

boot_part=$(ls -l /dev/disk/by-label | grep "boot" | grep -oE "$chosen_disk.*$")
if [ -z $boot_part ]; then
    echo "Failed to capture boot partition."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi

echo "Mount partition /dev/$boot_part."
mount "/dev/$boot_part" $mnt_boot
hdparm -z /dev/$chosen_disk
echo "Partition /dev/$boot_part mounted."

echo "Activate SSH..."
touch $mnt_boot/ssh
echo "SSH has been activated on $chosen_disk."

umount "/dev/$boot_part"
hdparm -z /dev/$chosen_disk
if [ -d $mnt_boot ]; then 
    rm -rf $mnt_boot
fi

cleanup_environment
echo "Script ended successfully."

exit