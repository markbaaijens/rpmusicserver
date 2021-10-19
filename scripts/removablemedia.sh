#!/bin/bash


# From: df
echo "==================================== MOUNT =============================================="
mounted=$(df | grep -E "^/dev/[ms]")
echo "$mounted"

# From: lsblk -b -e7
echo "================================== PARTITIONS ==========================================="
block=$(lsblk -b -e7 | grep -wv "rom")
echo "$block"

# From: ls -l /dev/disk/by-id
echo "==================================== MEDIA =============================================="
media=$(ls -l /dev/disk/by-id | cut -d':' -f2- | cut -d' ' -f2- | grep -Ewv -e "^[0-9]+" -e "^(ata|wwn)\-?" | grep -vE "\-part[1-9]")
media=$(echo "$media" | sed -e "s/\.\.\/\.\./\/dev/g" | rev | sed -e "s/_/ /g" | cut -d' ' -f1,4- | rev)
echo "$media"


# From: fdisk -l 
echo "==================================== DISKS =============================================="
disks=$(sudo fdisk -l | grep -oE "^Disk \/dev\/[ms].* bytes" | cut -d' ' -f 2- | sort | sed -e "s/://g")
echo "$disks"


# From: parted -l
echo "=================================== MODELS/DISK ========================================="
models=$(sudo parted -l | grep -E "^(Model|Disk /dev/[ms])" | tac | cut -d' ' -f2-)
echo "$models"


# From: lsusb
echo "=================================== REMOVABLE USB ======================================="
usb=$(lsusb | cut -d" " -f7- | grep -wv -e "[Hh]ub")
echo "$usb"
