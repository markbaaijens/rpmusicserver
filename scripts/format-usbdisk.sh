#!/bin/bash

# Ask user for disk to be formatted (see burn-image.sh)
# - filtered by USB?

# Ask user confirmation before formatting (see burn-image.sh)

# Wipe USB-disk
	# Wipe disk
	lsblk | grep disk
	sudo umount /dev/sda1
	sudo wipefs -a /dev/sda
	# Or: sudo dd if=/dev/zero of=/dev/sda bs=512 count=1 conv=notrunc
	sudo hdparm -z /dev/sda  # Alternative: sudo partprobe /dev/sda

# Format with ext4
# Attach label, fixed name = usbdisk
	# Create new partition table
	# Scripting fdisk  to create partition:
	#   n = new partition
	#   p = primary
	#   1 = Enter = nuber
	#   First sector: enter
	#   Last sector: enter
	#   w = write
	echo -e "o\nn\np\n1\n\n\nw" | sudo fdisk /dev/sda
	sudo hdparm -z /dev/sda
	lsblk  # Check
	
	# Format partition as ext4
	sudo mkfs.ext4 -L 'usbdata' /dev/sda1
	sudo hdparm -z /dev/sda
	# Check label:  sudo e2label /dev/sdXY
	