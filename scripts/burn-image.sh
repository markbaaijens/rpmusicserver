#!/bin/bash
# This script will burn the Raspbian OS Lite Image from the raspberrypi.org server and burn the image to a SD-card.
# The execution of the script is usually done by technical personnel with the...
#
# $ sudo chmod 770 ./burn.sh && sudo ./burn.sh
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

# download link to the raspian image
image=https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip

# name of the archive
archive=raspian-os-lite.zip

# wget log filename
wgetlog=wget-raspian.log



# === PROGRAM ===

# get the curl and wget app if not yet installed
apt install curl wget -y

# create a working directory in the /tmp folder to operate in
cd /tmp
[ ! -d /tmp/raspian ] && mkdir /tmp/raspian
cd raspian

# check whether image exists online
imagesize=$(curl -I $image | grep content-length | grep -oE '[0-9]+')
if [ -z "$imagesize" ] || [ $imagesize = 0 ]
then
  echo "Image $image not found."
  echo "Script ended."
  exit 4
fi

# get Raspian image online and its pid. download in the background so we can continue with other important stuff
#wgetpid=$(wget -b -c -P /tmp/raspian -o $wgetlog -O $archive --no-check-certificate $image | grep 'pid' | grep -oE '[0-9]+' )
wget -b -c -P /tmp/raspian -o $wgetlog -O $archive --no-check-certificate $image & wgetpid=`echo $!`
echo "Raspian image download pid = $wgetpid"

# user feedback: is required to prepare the process. user that placed the sd-card already has to remove it to gather a list of devices
echo "Be sure to leave the SD-card out of the computer. Press [Enter] when ready..."
read -n 1 -s -r

# in the meantime we want to know how long the download takes
duration=$(tail -n 2 $wgetlog | grep -oE '[^[:space:]]+$')
if [ "$duration" = "do." ]
then
  duration=""
  echo "$(tac $wgetlog | head -n 2)"
else
  echo "Duration: $(echo "$duration" | head -n 1)"
fi

# get list of initial storage devices
echo "$(lsblk | grep  -oE '^[^[:space:]]+' | grep -Evw -e NAME -e '^loop[0-9]+')" > initialblk.txt
echo "$(sort initialblk.txt)" > initialblk.txt

# user feedback: is required to confirm that the SD-card has been added
echo "Put the SD-card in the computer, wait for it to recognize he card. Press [Enter] when ready..."
read -n 1 -s -r

# get a new list of storage devices
echo "$(lsblk | grep  -oE '^[^[:space:]]+' | grep -Evw -e NAME -e '^loop[0-9]+')" > lsblk.txt
echo "$(sort lsblk.txt)" > lsblk.txt

# compare the lists and get the device that was added
sdcard=$(comm -13 initialblk.txt lsblk.txt)
# cleanup: remove the lists that were written in files
rm initialblk.txt
rm lsblk.txt

# if no difference between the two lists, exit
if [ -z "$sdcard" ]
then
  echo "No SD-card was added."
  echo "Script ended."
  exit 2
fi

# get the label and its partitions from the sd-card
sdlabel=$(echo "$sdcard" | head -n 1)
partitions=$(echo "$sdcard" | grep -vw "$sdlabel" | grep -oE "($sdlabel)p[0-9]+")

# unmount sd-card
for partition in $partitions; do
  echo "partition /dev/$partition unmounted..."
  umount "/dev/$partition"
done

# it is time to extract the archive, when the download is finished
if [ -n "$duration" ]
then
  duration=$(tail -n 2 $wgetlog | head -n 1 | grep -oE '[^[:space:]]+$')
  # did we capture a valid timestamp? yes? then wait till download is done, otherwise...start unzipping assuming the download has finished
  if [[ $duration =~ ^([0-9]+[ms])+$ ]]
  then
    echo "Waiting for the image ($duration time left)..."
#    wait $wgetpid
    sleep $duration
  fi
fi

# extract the downloaded image
unzip $archive

echo "Made up your mind? No problem, nothing is done yet with your SD-card."
read -r -p "Do you want to ABORT installatation on $sdlabel? [y/N]" response
if [[ "$response" =~ ^[yY]([eE][sS])?$ ]]
then
  # cleanup: leave /tmp as it were
  rm *
  cd ..
  rm -rf raspian

  echo "Script ended."
  exit 5
fi

# wipe SD-card
echo "Start wiping $sdlabel..."
#wipefs -a "/dev/$sdlabel"
echo "Done wiping $sdlabel."

apt install gddrescue -y
image=$(echo "${archive}" | sed -e 's/zip$/img/g')
echo "Start burning $image to $sdlabel..."
#ddrescue -d -D --force $image "/dev/$sdlabel"
echo "Done burning $sdlabel."

# cleanup: leave /tmp as it were
rm *
cd ..
rm -rf raspian

# make ssh default in install
bootpart=$(echo "$partitions" | head -n 1)
if [ -z "$bootpart" ]
then
  echo "SSH is NOT active."
  echo "Script ended."
  exit 0
fi

# mount SD-card
[ ! -d /media/boot ] && mkdir /media/boot
mount "/dev/$bootpart" /media/boot
echo "partition /dev/$bootpart mounted."
umount "/dev/$bootpart"
touch /media/boot/ssh
[ -d /media/boot ] && rm -rf /media/boot
echo "Script ended."

echo "SSH is active on $sdlabel."
echo
echo "Congrats! Process was successfully executed."
echo "It is now save to take the SD-card out of your computer."
echo "Insert SD-card in your Raspberry Pi and finish the installation."

exit 0
