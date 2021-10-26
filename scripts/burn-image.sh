#!/bin/bash
#
# This script will burn the Raspbian OS Lite Image from the raspberrypi.org server and burn the image to a SD-card.
#

if [ -z "$(whoami | grep root)" ]
then
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
    if [ ! -d $working_dir ]
    then 
        mkdir $working_dir
    fi
    export LC_ALL=C  # Console output = English
}

cleanup_environment() {
    echo "Cleaning up environment"
    rm -rf $working_dir
    # todo (discussion) Do we really want to remove the downloaded image (will slow down subsequent installations)
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
    model=$(parted /dev/$disk print | grep Model | cut -d " " -f2- )
    size=$(parted /dev/$disk print | grep Disk | awk '{print $3}')
    echo "$counter: $model /dev/$disk ($size) $([ $counter == 0 ] && echo "[default]")" # todo only the first item
    counter=$(($counter + 1))
done
echo "q: quit"

# todo q is not working
# todo menu item for quit
read -p "Select a disk by number or press [Enter] to choose the first one " disk_choice
echo "$disk_choice"
if [ "$disk_choice" == "q" ]; then
    echo "No disk selected."
    cleanup_environment    
    echo "Script ended with failure."
    exit
fi

chosen_disk=${sd_disks[disk_choice]}
echo "You have chosen: ${sd_disks[$chosen_disk]}"
sdcard="$(lsblk | grep ${sd_disks[$chosen_disk]})"

# get the label and its partitions from the sd-card
sdlabel=$(echo "$sdcard" | head -n 1)
echo "$sdlabel"
partitions=$(echo "$sdcard" | grep -vw "$sdlabel" | grep -oE "($sdlabel)p$number_pattern")
echo "$partitions"
exit
read -r -p "Do you want to start installation on $sdlabel? [yes/NO]" start_install
if [  ! start_install == yes ]  # todo pseudo-code
#if [ -z "$start_install" ] || [[ "$start_install" =~ ^[nN][oO]?$ ]]
then
    echo "Script aborted."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi

# unmount sd-card
echo "Unmounting /dev/$sdlabel partitions..."
for partition in $partitions; do
    # todo testen
    sleep 3
    if [ ! $(umount -f "/dev/$partition") ]
    then
        echo "Failed to umount /dev/$partition."
        cleanup_environment
        echo "Script ended with failure."
        exit
    fi
    echo "Partition /dev/$partition successfully unmounted."
done

if [ ! $(dpkg --list | grep wget | awk '{print $1}' | grep ii) ]
then 
    apt install wget -y
fi
echo "Downloading image..."
if [ ! $(wget -c --show-progress -P $working_dir -O $working_dir/$archive $image) ]
then
    echo "Command wget unsuccesful."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi
echo "Download complete"

# todo check downloaded image (hash)

# extract the downloaded image
echo "Extracting $working_dir/$archive..."
unzip -o $working_dir/$archive -d $working_dir
echo "Done extracting archive"
extracted_img=$(ls -t $working_dir/*.img | head -n 1)
if [ -z $extracted_img ]
then
    echo "No image found in $working_dir."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi

# wipe SD-card
echo "Start wiping $sdlabel..."
if [ ! $(wipefs -a "/dev/$sdlabel") ]
then
    echo "Command wipefs unsuccesful."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi
echo "Done wiping $sdlabel."

# burn SD-card
if [ ! $(dpkg --list | grep gddrescue | awk '{print $1}' | grep ii) ]
then 
    apt install gddrescue -y
fi
echo "Start burning $extracted_img to $sdlabel..."
if [ ! $(ddrescue -D --force $extracted_img "/dev/$sdlabel") ]
then
    echo "Command ddrescue unsuccesful."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi
echo "Done burning $sdlabel."

# mount SD-card and make ssh default in install
if [ ! -d $mnt_boot ] 
then 
    mkdir $mnt_boot
fi
boot_part=$(ls -l /dev/disk/by-label | grep "boot" | grep -oE "$sdlabel.*")
echo "Mount partition /dev/$boot_part."
if [ ! $(mount "/dev/$boot_part" $mnt_boot) ]
then
    echo "Command mount unsuccesful."
    cleanup_environment
    echo "Script ended with failure."
    exit
fi
echo "Partition /dev/$boot_part mounted."

echo "Activate SSH..."
if [ ! $(touch $mnt_boot/ssh) ] 
then
    echo "Command touch unsuccesful."
    echo "SSH cannot be activated on $sdlabel."
fi
echo "SSH has been activated on $sdlabel."

umount "/dev/$boot_part"
if [ -d $mnt_boot ]
then 
    rm -rf $mnt_boot
fi

cleanup_environment
echo "Script ended successfully."

exit
