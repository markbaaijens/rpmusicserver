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
mincap=0

# mount point for boot partition
mntboot=/media/boot



# === FUNCTIONS ===

lsstorage() {
  echo "$(lsblk -e7 | grep -v NAME)" > $1
  echo "$(sort $1)" > $1
}

cleanup() {
  rm -rf $1
}




# === PROGRAM ===

# get the curl and wget app if not yet installed
apt install curl wget -y

# check whether image exists online
imagesize=$(curl -I $image | grep content-length | grep -oE "[0-9]+")
if [ -z "$imagesize" ] || [ $imagesize -eq 0 ]
then
  echo "Image $image not found."
  echo "Script ended."
  exit 4
fi

# create a working directory in the /tmp folder to operate in
workingdir=$(echo "${workingdir}" | sed -e "s/\/$//g")
[ ! -d $workingdir ] && mkdir $workingdir

# get Raspbian image online and its pid. download in the background so we can continue with other important stuff
wget -b -c -P $workingdir -o $wgetlog -O $archive --no-check-certificate $image & wgetpid=`echo $!`
echo "Raspbian image download pid = $wgetpid"

# user feedback: is required to prepare the process. user that placed the sd-card already has to remove it to gather a list of devices
echo "Be sure to leave the SD-card out of the computer. Press [Enter] when ready..."
read -n 1 -s -r

# in the meantime we want to know how long the download takes
duration=$(tail -n 2 $workingdir/$wgetlog | grep -oE "[^[:space:]]+$")
if [ "$duration" = "do." ]
then
  duration=""
  echo "$(tac $workingdir/$wgetlog | head -n 2)"
else
  echo "Duration: $(echo "$duration" | head -n 1)"
fi

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
partitions=$(echo "$sdcard" | grep -vw "$sdlabel" | grep -oE "($sdlabel)p[0-9]+")

# validate storage capacity on SD-card
sdcapacity=$(df | grep "$sdlabel" | grep -oE "/dev/($sdlabel)p[0-9]+[[:space:]]+[0-9]+" | grep -oE "[^[:space:]]+" | grep -oE "^[0-9]+$" | paste -sd+ | bc)
if [ "$sdcapacity" -lt "$mincap" ]
then
  echo "Not enough storage on $sdlabel."
  cleanup $workingdir
  echo "Script ended."
  exit 2
fi

# unmount sd-card
for partition in $partitions; do
  umount "/dev/$partition"
  if [ -z "$(df | grep '/dev/$partition')" ]
  then
    echo "partition /dev/$partition successfully unmounted."
  else
    echo "failed to umount /dev/$partition."
    cleanup $workingdir
    echo "Script ended."
    exit 5
  fi
done

# it is time to extract the archive, when the download is finished
if [ -n "$duration" ]
then
  duration=$(tail -n 2 $workingdir/$wgetlog | head -n 1 | grep -oE "[^[:space:]]+$")
  # did we capture a valid timestamp? yes? then wait till download is done, otherwise...start unzipping assuming the download has finished
  if [[ $duration =~ ^([0-9]+[ms])+$ ]]
  then
    echo "Waiting for the image ($duration time left)..."
#    wait $wgetpid
    sleep $duration
  fi
fi

# extract the downloaded image
unzip $workingdir/$archive

echo "Made up your mind? No problem, nothing is done yet with your SD-card."
read -r -p "Do you want to start installation on $sdlabel? [y/N]" startinstall
if [ -z "$startinstall" ] || [[ "$startinstall" =~ ^[nN]([oO])?$ ]]
then
  cleanup $workingdir
  echo "Script ended."
  exit 5
fi

# wipe SD-card
echo "Start wiping $sdlabel..."
#wipefs -a "/dev/$sdlabel"
echo "Done wiping $sdlabel."

apt install gddrescue -y
image=$(echo "${archive}" | sed -e "s/zip$/img/g")
echo "Start burning $image to $sdlabel..."
#ddrescue -d -D --force $image "/dev/$sdlabel"
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
echo "Insert SD-card in your Raspberry Pi and finish the installation."

exit 0
