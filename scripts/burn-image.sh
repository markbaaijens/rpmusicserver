#!/bin/bash

if [ -z "$(whoami | grep root)" ]; then
    echo "Not running as root."
    echo "Script ended with failure."
    exit
fi

working_dir=/tmp/raspbian
image=https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-11-08/2021-10-30-raspios-bullseye-armhf-lite.zip
image_hash="008d7377b8c8b853a6663448a3f7688ba98e2805949127a1d9e8859ff96ee1a9"
archive=raspbian-os-lite.zip
number_pattern="[0-9]+"
mount_point=/mnt/temp

setup_environment() {
    if [ ! -d $working_dir ]; then 
        mkdir $working_dir
    fi
    export LC_ALL=C  # Console output = English
}

cleanup_environment() {
    unset LC_ALL  # Reset console output to default language
}

mount_partition () {
    echo "Mounting partition /dev/$partition."
    if [ ! -d $mount_point ]; then 
        mkdir $mount_point
    fi

    if [ -z $partition ]; then
        echo "Failed to capture $partition."
        cleanup_environment
        echo "Script ended with failure."
        exit
    fi

    mount "/dev/$partition" $mount_point
    hdparm -z /dev/$chosen_disk
    echo "Partition /dev/$partition mounted."
}

unmount_partition () {
    umount "/dev/$partition"
    hdparm -z /dev/$chosen_disk
    if [ -d $mount_point ]; then 
        rm -rf $mount_point
    fi
    sleep 3 # Give the OS time to reread
    echo "Partition /dev/$partition unmounted."
}

setup_environment

readarray -t disks < <(lsblk -b -e7 -o name,type | grep disk | awk '{print $1}')
sd_disks=()
for disk in "${disks[@]}"; do
    model=$(parted /dev/$disk print | grep Model)
    sd_disks+=("$disk")
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
    echo "$counter: $model /dev/$disk ($size)"
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
size=$(parted /dev/$chosen_disk print | grep "Disk /dev/" | awk '{print $3}')
echo "You have chosen: $chosen_disk ($size)"

# Variable $size returns a string like 32.2GB (or MB or KB)
size_val=${size%??}  # Extract the pure value
size_val=${size_val%.*} # Convert to int, bash cannot handle floats
size_id=${size: -2} # Extract Indentifier KB. MB or GB in the last two characters

# We check against KB so we must recalculate in case size is given in MB of GB 
if [ "$size_id" == "MB" ]; then
    size_kb=$(($size_val * 1024))
fi
if [ "$size_id" == "GB" ]; then
    size_kb=$(($size_val * 1024 * 1024))
fi

minsize_kb=$((1024 * 1024 * 7))  # approximately 8GB in KB
if [ $size_kb -lt $minsize_kb ]; then
    echo "Error: SD-card has insufficient capacity. Minimum size is 8GB."
    cleanup_environment    
    echo "Script ended."
    exit
fi

echo "Image-type:"
echo "P: Production (hostname = rpms)"
echo "D: Development (hostname = rpmsdev)"
echo "Q: quit"

read -p "Select a type: " type_choice

if [ "${type_choice,,}" == "q" ]; then
    cleanup_environment    
    echo "Script ended by user."
    exit
fi

if [ "$type_choice" == "" ]; then
    echo "No type selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi
if [ ${type_choice,,} != "p" ] && [ ${type_choice,,} != "d" ]; then
    echo "No type selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi
echo "You have chosen: $type_choice $([ ${type_choice,,} == "p" ] && echo "=> production" || echo "=> development")"

echo "Language:"
echo "E: English"
echo "D: Dutch"
echo "Q: quit"

read -p "Select a language: " lang_choice

if [ "${lang_choice,,}" == "q" ]; then
    cleanup_environment    
    echo "Script ended by user."
    exit
fi

if [ "$lang_choice" == "" ]; then
    echo "No language selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi
if [ ${lang_choice,,} != "e" ] && [ ${lang_choice,,} != "dd" ]; then
    echo "No language selected."
    cleanup_environment    
    echo "Script ended."
    exit
fi
echo "You have chosen: $lang_choice $([ ${lang_choice,,} == "e" ] && echo "=> English" || echo "=> Dutch")"

read -r -p "Do you want to continue burning on $chosen_disk? [yes/NO] " start_install
if [ "$start_install" != "yes" ]; then
    cleanup_environment
    echo "Script ended by user."
    exit
fi

if [ ! $(dpkg --list | grep wget | awk '{print $1}' | grep ii) ]; then 
    apt install wget -y
fi
echo "Downloading image..."
wget -c --show-progress -P $working_dir -O $working_dir/$archive $image
echo " => download complete"

if [ "$(sha256sum $working_dir/$archive | cut -d' ' -f1)" != "$image_hash" ]; then
    echo "Checksum of the downloaded image $archive failed."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi
echo "Checksum of the downloaded image $archive is OK."

echo "Extracting $working_dir/$archive..."
unzip -o $working_dir/$archive -d $working_dir
extracted_img=$(ls -t $working_dir/*.img | head -n 1)
if [ -z $extracted_img ]; then
    echo "No image found in $working_dir."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi
echo " => done extracting $working_dir/$archive"

echo "Unmounting /dev/$chosen_disk partitions..."
partitions=$(lsblk -l -n -p -e7 /dev/$chosen_disk | grep part | awk '{print $1}')
for partition in $partitions; do
    sleep 3
    umount -f "$partition"
	if [ -n "$(df | grep $partition)" ]; then
        echo "Failed to umount $partition."
        cleanup_environment
        echo "Script ended with failure."
        exit
    fi
   	echo "Partition $partition successfully unmounted."
done
hdparm -z /dev/$chosen_disk
echo " => done unmounting /dev/$chosen_disk partitions"

echo "Start wiping $chosen_disk..."
wipefs -a "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk
echo " => done wiping $chosen_disk."

if [ ! $(dpkg --list | grep gddrescue | awk '{print $1}' | grep ii) ]; then 
    apt install gddrescue -y
fi
echo "Start burning $extracted_img to $chosen_disk..."
ddrescue -D --force $extracted_img "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk
sleep 3  # Give the OS some time to reread
echo " => done burning $chosen_disk."

if [ ! -d /dev/disk/by-label ]; then
	echo "/dev/disk/by-label doesn't exist"
    cleanup_environment
    echo "Script ended with failure."
    exit
fi

echo "Activate SSH..."
partition=$(ls -l /dev/disk/by-label | grep "boot" | grep -oE "$chosen_disk.*$")
mount_partition
touch $mount_point/ssh
unmount_partition
echo " => SSH has been activated on $chosen_disk."

if [ ${type_choice,,} == "p" ]; then
    hostname="rpms"
else
    hostname="rpmsdev"
fi
echo "Change hostname to $hostname..."
partition=$(ls -l /dev/disk/by-label | grep "rootfs" | grep -oE "$chosen_disk.*$")
mount_partition
sed -i -e "s/raspberrypi/$hostname/g" $mount_point/etc/hostname
sed -i -e "s/raspberrypi/$hostname/g" $mount_point/etc/hosts
unmount_partition
echo " => done changing hostname."

case ${lang_choice,,} in
"e")
    langcode="EN"
    ;;
"n")
    langcode="NL"
    ;;
esac
echo "Set language..."
partition=$(ls -l /dev/disk/by-label | grep "rootfs" | grep -oE "$chosen_disk.*$")
mount_partition
echo $langcode > /etc/language.txt
unmount_partition
echo " => language has been set to $lang_choice."

cleanup_environment
echo "Script ended successfully."

exit
