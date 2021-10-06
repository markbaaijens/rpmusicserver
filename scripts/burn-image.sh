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

# set logfile to record progress (use tail -f <filename> in seperate terminal)
log=/var/log/raspbian/burn-image.log

# download link to the Raspbian image
image=https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip

# name of the archive
archive=raspbian-os-lite.zip

# wget log filename
wgetlog=wget-raspbian.log

# minimal capacity required on SD-card (0 has no minimum)
mincap=1900000000

# mount point for boot partition
mntboot=/mnt/boot




# === REGULAR EXPRESSION PATTERNS ===

# numbers
numberpattern="[0-9]+"

# non-space
negmultiplespacepattern="[^[:space:]]+"




# === FUNCTIONS ===

lsstorage() {
  echo "$(lsblk -b -e7 -o name | grep -v NAME)" > $1
  echo "$(sort $1)" > $1
}

cleanup() {
  echo "Cleaning up $1..." | tee -a $log
  rm -rf $1
}




# === PROGRAM ===

# create logfile
[ ! -d $(dirname $log) ] && mkdir $(dirname $log)
[ ! -f $log ] && touch $log && echo " " >> $log
echo "[$(date)] Start" >> $log

# get the curl and wget app if not yet installed
apt install curl wget -y

# check whether image exists online
imagesize=$(curl -I $image | grep content-length | grep -oE "$numberpattern")
if [ -z "$imagesize" ] || [ $imagesize -eq 0 ]
then
  echo "Image $image not found." | tee -a $log
  echo "Script ended." | tee -a $log
  exit 4
fi

# create a working directory in the /tmp folder to operate in
workingdir=$(echo "$workingdir" | sed -e "s/\/$//g")
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

# if no difference between the two lists, exit
if [ -z "$sdcard" ]
then
  echo "No SD-card was added." | tee -a $log
  cleanup $workingdir
  echo "Script ended." | tee -a $log
  exit 2
fi
echo "SD-card to burn has been detected..." | tee -a $log
echo "$sdcard" >> $log

# get the label and its partitions from the sd-card
sdlabel=$(echo "$sdcard" | head -n 1)
partitions=$(echo "$sdcard" | grep -vw "$sdlabel" | grep -oE "($sdlabel)p$numberpattern")

# validate storage capacity on SD-card
#sdcapacity=$(df -B1 | grep "$sdlabel" | grep -oE "/dev/($sdlabel)p$numberpattern[[:space:]]+$numberpattern" | grep -oE "$negmultiplespacepattern" | grep -oE "^$numberpattern$" | paste -sd+ | bc)
sdcapacity=$(lsblk -b -e7 -o name,size | grep -w "^$sdlabel" | grep -oEw "$numberpattern")
if [ $sdcapacity -lt $mincap ]
then
  echo "Not enough storage on $sdlabel." | tee -a $log
  echo "$mincap Byte required;" | tee -a $log
  echo "$sdcapacity Byte found." | tee -a $log
  cleanup $workingdir
  echo "Script ended." | tee -a $log
  exit 2
fi

# unmount sd-card
echo "Unmounting /dev/$sdlabel partitions..." | tee -a $log
for partition in $partitions; do
  sleep 5
  umount -f "/dev/$partition"

  if [ -z "$(df | grep '/dev/$partition')" ]
  then
    echo "[ $(date) ] Partition /dev/$partition successfully unmounted." | tee -a $log
  else
    echo "[ $(date) ] Failed to umount /dev/$partition." | tee -a $log
    cleanup $workingdir
    echo "Script ended." | tee -a $log
    exit 5
  fi
done

echo "[ $(date) ] Downloading image..." | tee -a $log
# get Raspbian image online and its pid. download in the background so we can continue with other important stuff
# dummy: $ wget -c -O raspbian-os-lite.zip --no-check-certificate https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip
wget -c --show-progress -P $workingdir -o $workingdir/$wgetlog -O $workingdir/$archive --no-check-certificate $image
echo "[ $(date) ] Download complete" | tee -a $log

# check whether the extraced image would fit on the SD-card
extractedimgsize=$(unzip -l $workingdir/$archive | tac | head -n 1 | grep -oE "^$numberpattern")
if [ -z "$extractedimgsize" ] || [ $sdcapacity -lt $extractedimgsize ]
then
  echo "Not enough storage on $sdlabel." | tee -a $log
  echo "$extractedimgsize Byte required;" | tee -a $log
  echo "$sdcapacity Byte found." | tee -a $log
  cleanup $workingdir
  echo "Script ended." | tee -a $log
  exit 2
fi

# extract the downloaded image
echo "[ $(date) ] Extracting $workingdir/$archive..." | tee -a $log
unzip -o $workingdir/$archive -d $workingdir
echo "[ $(date) ] Done extracting archive" | tee -a $log
extractedimg=$(ls -t $workingdir/*.img | head -n 1)
if [ -z $extractedimg ]
then
  echo "No image found in $workingdir." | tee -a $log
  cleanup $workingdir
  echo "Script ended." | tee -a $log
  exit 2
fi

echo "Made up your mind? No problem, nothing is done yet with your SD-card."
read -r -p "Do you want to start installation on $sdlabel? [y/N]" startinstall
if [ -z "$startinstall" ] || [[ "$startinstall" =~ ^[nN][oO]?$ ]]
then
  echo "Script aborted by $(whoami)" | tee -a $log
  cleanup $workingdir
  echo "Script ended." | tee -a $log
  exit 5
fi

# wipe SD-card
echo "[ $(date) ] Start wiping $sdlabel..." | tee -a $log
wipefs -a "/dev/$sdlabel"
#wipefsresult=$
#echo "$wipefsresult" | tee -a $log
echo "[ $(date) ] Done wiping $sdlabel." | tee -a $log

# burn SD-card
apt install gddrescue -y
echo "[ $(date) ] Start burning $extractedimg to $sdlabel..." | tee -a $log
ddrescue -D --force $extractedimg "/dev/$sdlabel"
#ddresult=$
#echo "$ddresult" | tee -a $log
echo "[ $(date) ] Done burning $sdlabel." | tee -a $log

cleanup $workingdir

# find the boot partition
bootpart=$(ls -l /dev/disk/by-label | grep "boot" | grep -oE "$sdlabel.*")
if [ -z "$bootpart" ]
then
  echo "SSH is NOT active." | tee -a $log
  echo "Script ended." | tee -a $log
  exit 0
fi

# mount SD-card and
# make ssh default in install
[ ! -d $mntboot ] && mkdir $mntboot
mount "/dev/$bootpart" $mntboot
echo "partition /dev/$bootpart mounted." | tee -a $log
echo "Activate SSH..." | tee -a $log
touch $mntboot/ssh
if [ -f "$mntboot/ssh" ]
then
  echo "SSH is active on $sdlabel." | tee -a $log
else
  echo "SSH is NOT active." | tee -a $log
fi
umount "/dev/$bootpart"
[ -d $mntboot ] && rm -rf $mntboot
echo "Script ended." | tee -a $log

echo
echo "Congrats! Process was successfully executed." | tee -a $log
echo "It is now save to take the SD-card out of your computer."
echo "Insert SD-card in your 64-bit (!) Raspberry Pi and finish the installation." | tee -a $log

exit 0
