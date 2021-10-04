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

# set working directory
workingdir=/tmp/raspbian

# download link to the Raspbian image
image=https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip

# name of the archive
archive=raspbian-os-lite.zip

# wget log filename
wgetlog=wget-raspbian.log

# minimal capacity required on SD-card (0 has no minimum)
mincap=1900000000

# mount point for boot partition
mntboot=/media/boot




# === REGULAR EXPRESSION PATTERNS ===

# numbers
numberpattern="[0-9]+"

# non-space
negmultiplespacepattern="[^[:space:]]+"

# timeformat
timeformatpattern="^([0-9]{,2}[hms])+$"




# === FUNCTIONS ===

lsstorage() {
  echo "$(lsblk -b -e7 -o name | grep -v NAME)" > $1
  echo "$(sort $1)" > $1
}

cleanup() {
  rm -rf $1
}




# === PROGRAM ===

# get the curl and wget app if not yet installed
apt install curl wget -y

# check whether image exists online
imagesize=$(curl -I $image | grep content-length | grep -oE "$numberpattern")
if [ -z "$imagesize" ] || [ $imagesize -eq 0 ]
then
  echo "Image $image not found."
  echo "Script ended."
  exit 4
fi

# create a working directory in the /tmp folder to operate in
workingdir=$(echo "${workingdir}" | sed -e "s/\/$//g")
[ ! -d $workingdir ] && mkdir $workingdir

# user feedback: is required to prepare the process. user that placed the sd-card already has to remove it to gather a list of devices
echo "Be sure to leave the SD-card out of the computer. Press [Enter] when ready..."
read -n 1 -s -r

# get list of initial storage devices
lsstorage $workingdir/initialblk.txt

# user feedback: is required to confirm that the SD-card has been added
echo "Put the SD-card in the computer, wait for it to recognize and automount the card. Press [Enter] when ready..."
read -n 1 -s -r

# get a new list of storage devices
lsstorage $workingdir/lsblk.txt

# compare the lists and get the device that was added
sdcard=$(comm -13 $workingdir/initialblk.txt $workingdir/lsblk.txt)
# cleanup: remove the lists that were written in files
rm $workingdir/initialblk.txt
rm $workingdir/lsblk.txt

# if no difference between the two lists, exit
if [ -z "$sdcard" ]
then
  echo "No SD-card was added."
  cleanup $workingdir
  echo "Script ended."
  exit 2
fi

# get the label and its partitions from the sd-card
sdlabel=$(echo "$sdcard" | head -n 1)
partitions=$(echo "$sdcard" | grep -vw "$sdlabel" | grep -oE "($sdlabel)p$numberpattern")

# validate storage capacity on SD-card
#sdcapacity=$(df -B1 | grep "$sdlabel" | grep -oE "/dev/($sdlabel)p$numberpattern[[:space:]]+$numberpattern" | grep -oE "$negmultiplespacepattern" | grep -oE "^$numberpattern$" | paste -sd+ | bc)
sdcapacity=$(lsblk -b -e7 -o name,size | grep -w "^$sdlabel" | grep -oEw "$numberpattern")
if [ $sdcapacity -lt $mincap ]
then
  echo "Not enough storage on $sdlabel."
  echo "$mincap Byte required;"
  echo "$sdcapacity Byte found."
  cleanup $workingdir
  echo "Script ended."
  exit 2
fi

# unmount sd-card
for partition in $partitions; do
  umount "/dev/$partition"
  umntresult=$
  echo "$umntresult"
  if [ $umntresult -eq 0 ] [ -z "$(df | grep '/dev/$partition')" ]
  then
    echo "partition /dev/$partition successfully unmounted."
  else
    echo "failed to umount /dev/$partition."
    cleanup $workingdir
    echo "Script ended."
    exit 5
  fi
done

# get Raspbian image online and its pid. download in the background so we can continue with other important stuff
# dummy: $ wget -c -O raspbian-os-lite.zip --no-check-certificate https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip
wget -c --show-progress -P $workingdir -o $workingdir/$wgetlog -O $workingdir/$archive --no-check-certificate $image

# check whether the extraced image would fit on the SD-card
extractedimgsize=$(unzip -l $workingdir/$archive | tac | head -n 1 | grep -oE "^$numberpattern")
if [ -z "$extractedimgsize" ] || [ $sdcapacity -lt $extractedimgsize ]
then
  echo "Not enough storage on $sdlabel."
  echo "$extractedimgsize Byte required;"
  echo "$sdcapacity Byte found."
  cleanup $workingdir
  echo "Script ended."
  exit 2
fi

# extract the downloaded image
echo "extracting $workingdir/$archive..."
unzip -o $workingdir/$archive -d $workingdir
extractedimg=$(ls $workingdir/*.img | head -n 1)
if [ -z $extractedimg ]
then
  echo "No image found in $workingdir."
  cleanup $workingdir
  echo "Script ended."
  exit 2
fi

echo "Made up your mind? No problem, nothing is done yet with your SD-card."
read -r -p "Do you want to start installation on $sdlabel? [y/N]" startinstall
if [ -z "$startinstall" ] || [[ "$startinstall" =~ ^[nN][oO]?$ ]]
then
  cleanup $workingdir
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

cleanup $workingdir

# make ssh default in install
bootpart=$(echo "$partitions" | head -n 1)
if [ -z "$bootpart" ]
then
  echo "SSH is NOT active."
  echo "Script ended."
  exit 0
fi

# mount SD-card
[ ! -d $mntboot ] && mkdir $mntboot
mount "/dev/$bootpart" $mntboot
echo "partition /dev/$bootpart mounted."
umount "/dev/$bootpart"
touch $mntboot/ssh
[ -d $mntboot ] && rm -rf $mntboot
echo "Script ended."

echo "SSH is active on $sdlabel."
echo
echo "Congrats! Process was successfully executed."
echo "It is now save to take the SD-card out of your computer."
echo "Insert SD-card in your 64-bit (!) Raspberry Pi and finish the installation."

exit 0
