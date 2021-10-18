#!/bin/bash
# This script will burn the Raspbian OS Lite Image from the raspberrypi.org server and burn the image to a SD-card.
# The execution of the script is usually done by technical personnel with the...
#
# $ sudo chmod 770 ./burn-image.sh && sudo ./burn-image.sh
#
# ...on a computer with a SD-card reader.
# You have to know what you are doing and we don’t take any responsibility for data loss.

# check whether script runs from a superuser (sudo)
if [ -z "$(whoami | grep root)" ]
then
  echo "Not running as root."
  echo "Script ended."
  exit 1    
fi




# === GENERAL SETTINGS ===
workingdir=/tmp/raspbian
image=https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip
archive=raspbian-os-lite.zip
wgetlog=wget-raspbian.log
mntboot=/mnt/boot




# === REGULAR EXPRESSION PATTERNS ===
numberpattern="[0-9]+"
negmultiplespacepattern="[^[:space:]]+"




# === FUNCTIONS ===

lsstorage() {
  echo "$(lsblk -b -e7 -o name | grep -v NAME)" > $1
  echo "$(sort $1)" > $1
}

cleanupworkingdir() {
  echo "Cleaning up $workingdir..."
  rm -rf $workingdir
}




# === PROGRAM ===

# get the wget app if not yet installed
apt install wget -y

# create a working directory in the /tmp folder to operate in
[ ! -d $workingdir ] && mkdir $workingdir

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
    model=$(parted /dev/$disk print | grep Model | awk '{print $2}')
    if [[ $model == *"SD"* ]]; then
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
    model=$(parted /dev/$disk print | grep Model | awk '{print $2}')
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
echo "You have chosen: ${disks[$chosen_disk]}"

sdcard=$chosen_disk

# get the label and its partitions from the sd-card
sdlabel=$(echo "$sdcard" | head -n 1)
partitions=$(echo "$sdcard" | grep -vw "$sdlabel" | grep -oE "($sdlabel)p$numberpattern")

# unmount sd-card
echo "Unmounting /dev/$sdlabel partitions..."
for partition in $partitions; do
  sleep 3
  umount -f "/dev/$partition"

  if [ -z "$(df | grep /dev/$partition)" ]
  then
    echo " Partition /dev/$partition successfully unmounted."
  else
    echo "Failed to umount /dev/$partition."
    cleanupworkingdir
    echo "Script ended."
    exit 5
  fi
done

echo "Downloading image..."
# get Raspbian image online
# dummy: $ wget -c -O raspbian-os-lite.zip --no-check-certificate https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip
wget -c --show-progress -P $workingdir -o $workingdir/$wgetlog -O $workingdir/$archive --no-check-certificate $image
echo "Download complete"

# check downloaded image (hash)

# check whether the extracted image would fit on the SD-card
extractedimgsize=$(unzip -l $workingdir/$archive | tac | head -n 1 | grep -oE "^$numberpattern")
if [ -z "$extractedimgsize" ] || [ $sdcapacity -lt $extractedimgsize ]
then
  echo "Not enough storage on $sdlabel."
  echo "$extractedimgsize Byte required;"
  echo "$sdcapacity Byte found."
  cleanupworkingdir
  echo "Script ended."
  exit 2
fi

# extract the downloaded image
echo "Extracting $workingdir/$archive..."
unzip -o $workingdir/$archive -d $workingdir
echo "Done extracting archive"
extractedimg=$(ls -t $workingdir/*.img | head -n 1)
if [ -z $extractedimg ]
then
  echo "No image found in $workingdir."
  cleanupworkingdir
  echo "Script ended."
  exit 2
fi

echo "Made up your mind? No problem, nothing is done yet with your SD-card."
read -r -p "Do you want to start installation on $sdlabel? [y/N]" startinstall
if [ -z "$startinstall" ] || [[ "$startinstall" =~ ^[nN][oO]?$ ]]
then
  echo "Script aborted by $(whoami)"
  cleanupworkingdir
  echo "Script ended."
  exit 5
fi

# wipe SD-card
echo "Start wiping $sdlabel..."
wipefs -a "/dev/$sdlabel"
#wipefsresult=$
#echo "$wipefsresult"
echo "Done wiping $sdlabel."

# burn SD-card
apt install gddrescue -y
echo "Start burning $extractedimg to $sdlabel..."
ddrescue -D --force $extractedimg "/dev/$sdlabel"
#ddresult=$
#echo "$ddresult"
echo "Done burning $sdlabel."

cleanupworkingdir

# find the boot partition
bootpart=$(ls -l /dev/disk/by-label | grep "boot" | grep -oE "$sdlabel.*")
if [ -z "$bootpart" ]
then
  echo "No boot partition found. SSH is not avaiilable."
  echo "Script ended."
  exit 0
fi

# mount SD-card and
# make ssh default in install
[ ! -d $mntboot ] && mkdir $mntboot
mount "/dev/$bootpart" $mntboot
echo "Partition /dev/$bootpart mounted."
echo "Activate SSH..."
touch $mntboot/ssh
if [ -f "$mntboot/ssh" ]
then
  echo "SSH is available on $sdlabel."
else
  echo "SSH is NOT available."
fi
umount "/dev/$bootpart"
[ -d $mntboot ] && rm -rf $mntboot
echo "Script ended."

echo
echo "Congrats! Process was successfully executed."
echo "It is now save to take the SD-card out of your computer."
echo "Insert SD-card in your 64-bit (!) Raspberry Pi and finish the installation."

exit 0
