#!/bin/bash

if [ -z "$(whoami | grep root)" ]; then
    echo "Not running as root"
    echo "Script ended with failure"
    exit
fi

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
    partition_name=$(ls -l /dev/disk/by-label | grep "$1" | grep -oE "$chosen_disk.*$")

    if [ ! -d $mount_point ]; then 
        mkdir $mount_point
    fi

    if [ -z $partition_name ]; then
        echo "Failed to capture $partition_name"
        cleanup_environment
        echo "Script ended with failure"
        exit
    fi

    mount "/dev/$partition_name" $mount_point

	if [ -z "$(df | grep $partition_name)" ]; then
        echo "Failed to mount $partition_name"
        cleanup_environment
        echo "Script ended with failure"
        exit
    fi
}

unmount_partition () {
    partition_name=$(ls -l /dev/disk/by-label | grep "$1" | grep -oE "$chosen_disk.*$")

    umount "/dev/$partition_name"
    hdparm -z /dev/$chosen_disk > /dev/null
    if [ -d $mount_point ]; then 
        rm -rf $mount_point
    fi
    sleep 3 # Give the OS time to reread

	if [ -n "$(df | grep $partition_name)" ]; then
        echo "Failed to umount $partition_name"
        cleanup_environment
        echo "Script ended with failure"
        exit
    fi
}

working_dir=/tmp/raspbian
image=https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2022-01-28/2022-01-28-raspios-bullseye-arm64-lite.zip
image_hash="d694d2838018cf0d152fe81031dba83182cee79f785c033844b520d222ac12f5"
archive=raspbian-os-lite.zip
number_pattern="[0-9]+"
mount_point=/mnt/temp

setup_environment

readarray -t disks < <(lsblk -b -e7 -o name,type | grep disk | awk '{print $1}')
sd_disks=()
for disk in "${disks[@]}"; do
    sd_disks+=("$disk")
done

if [ "${sd_disks[0]}" == "" ]; then
    echo "No disk available"
    cleanup_environment
    echo "Script ended with failure" 
    exit
fi

echo "Available disk(s):"
counter=0
for disk in "${sd_disks[@]}"; do
    model=$(parted -s /dev/$disk print | grep "Model" | cut -d " " -f2- )
    size=$(parted -s /dev/$disk print | grep "Disk /dev/" | awk '{print $3}')
    echo "$counter: $model /dev/$disk ($size)"
    counter=$(($counter + 1))
done
echo "Q: quit"

read -p "Select a disk: " disk_choice

if [ "${disk_choice,,}" == "q" ]; then
    cleanup_environment    
    echo "Script ended by user"
    exit
fi

if [ "$disk_choice" == "" ] || [ "${sd_disks[disk_choice]}" == "" ]; then
    echo "No disk selected"
    cleanup_environment    
    echo "Script ended"
    exit
fi

chosen_disk=${sd_disks[disk_choice]}
size=$(parted -s /dev/$chosen_disk print | grep "Disk /dev/" | awk '{print $3}')
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

minsize_kb=$((1024 * 1024 * 14))  # approximately 16GB in KB
if [ $size_kb -lt $minsize_kb ]; then
    echo "Error: SD-card has insufficient capacity. Minimum size is 16GB"
    cleanup_environment    
    echo "Script ended"
    exit
fi

echo "Image-type:"
echo "P: Production (hostname = rpms)"
echo "D: Development (hostname = rpmsdev)"
echo "Q: quit"

read -p "Select a type: " type_choice

if [ "${type_choice,,}" == "q" ]; then
    cleanup_environment    
    echo "Script ended by user"
    exit
fi

if [ "$type_choice" == "" ]; then
    echo "No type selected"
    cleanup_environment    
    echo "Script ended"
    exit
fi
if [ ${type_choice,,} != "p" ] && [ ${type_choice,,} != "d" ]; then
    echo "No type selected"
    cleanup_environment    
    echo "Script ended"
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
    echo "Script ended by user"
    exit
fi

if [ "$lang_choice" == "" ]; then
    echo "No language selected"
    cleanup_environment    
    echo "Script ended"
    exit
fi
if [ ${lang_choice,,} != "e" ] && [ ${lang_choice,,} != "d" ]; then
    echo "No language selected"
    cleanup_environment    
    echo "Script ended"
    exit
fi
echo "You have chosen: $lang_choice $([ ${lang_choice,,} == "e" ] && echo "=> English" || echo "=> Dutch")"

read -r -p "Do you want to continue burning on $chosen_disk? [yes/NO] " start_install
if [ "$start_install" != "yes" ]; then
    cleanup_environment
    echo "Script ended by user"
    exit
fi

if [ ! $(dpkg --list | grep wget | awk '{print $1}' | grep ii) ]; then 
    apt install wget -y
fi
echo "Downloading image..."
wget -c --show-progress -P $working_dir -O $working_dir/$archive $image
echo "... download complete"

if [ "$(sha256sum $working_dir/$archive | cut -d' ' -f1)" != "$image_hash" ]; then
    echo "Checksum of the downloaded image $archive failed"
    cleanup_environment
    echo "Script ended with failure"
    exit
fi
echo "Checksum of the downloaded image $archive is OK"

echo "Extracting $working_dir/$archive..."
unzip -o $working_dir/$archive -d $working_dir
extracted_img=$(ls -t $working_dir/*.img | head -n 1)
if [ -z $extracted_img ]; then
    echo "No image found in $working_dir"
    cleanup_environment
    echo "Script ended with failure"
    exit
fi
echo "... done extracting $working_dir/$archive"

echo "Unmounting /dev/$chosen_disk partitions..."
# partitions_bylabel=$(ls -l /dev/disk/by-label | grep -oE "$chosen_disk.*$"  | awk '{print $9}')
partitions=$(lsblk -l -n -p -e7 /dev/$chosen_disk | grep part | awk '{print $1}')
for partition in $partitions; do
    partition_name=$(echo $partition | sed -e "s/\/dev\///g")
    partition_label=$(ls -l /dev/disk/by-label | grep $partition_name | awk '{print $9}')
    unmount_partition "$partition_label"
   	echo "- partition $partition_label successfully unmounted"
done
hdparm -z /dev/$chosen_disk > /dev/null
echo "... done unmounting /dev/$chosen_disk partitions"
exit # todo

echo "Start wiping $chosen_disk..."
wipefs -a "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk > /dev/null
echo "... done wiping $chosen_disk"

if [ ! $(dpkg --list | grep gddrescue | awk '{print $1}' | grep ii) ]; then 
    apt install gddrescue -y
fi
echo "Start burning $extracted_img to $chosen_disk..."
ddrescue -D --force $extracted_img "/dev/$chosen_disk"
hdparm -z /dev/$chosen_disk > /dev/null
sleep 3  # Give the OS some time to reread
echo "... done burning $chosen_disk"

if [ ! -d /dev/disk/by-label ]; then
	echo "/dev/disk/by-label doesn't exist"
    cleanup_environment
    echo "Script ended with failure"
    exit
fi

echo "Activate SSH..."
mount_partition "boot"
touch $mount_point/ssh
unmount_partition "boot"
echo "... SSH has been activated on $chosen_disk"

if [ ${type_choice,,} == "p" ]; then
    hostname="rpms"
else
    hostname="rpmsdev"
fi
echo "Change hostname to $hostname..."
mount_partition "rootfs"
sed -i -e "s/raspberrypi/$hostname/g" $mount_point/etc/hostname
sed -i -e "s/raspberrypi/$hostname/g" $mount_point/etc/hosts
unmount_partition "rootfs"
echo "... done changing hostname"

echo "Set language..."
lang_choice=${lang_choice,,}
mount_partition "rootfs"
echo $lang_choice > $mount_point/etc/lang-choice.txt
unmount_partition "rootfs"
echo "... language has been set to $lang_choice."

cleanup_environment
echo "Script ended successfully"

exit
