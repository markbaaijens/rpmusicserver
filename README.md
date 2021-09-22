# rpmusicserver
Transform a Raspberry Pi in a music server with LMS (Squeezebox), Samba, transcoder, etc.

## Steps to turn a Pi into a music server:
* burn sd-kaart via burn-image script
* format usb-disk (ext4) by format-usbdisk script, label = usbdisk
* reboot the clean system
* install ssh (standard in Raspian?)
* remote installatie with install-rp script via ssh
	* ssh root@remoteServer "bash -s" < install-rp
* reboot

## Questions and decisions
* OS: raspian or ubuntu? => Raspian
* is ssh present in a fresh install of raspian?
* mount through fstab of rc.local? => fstab
* fixed ip-adres? => no (samba-acces by hostname)
* swap-file? => no
* install by install-rp script when root password is not yet configured?
* docker installation by standard repo? => yes
* config rp via sudo raspi-config?
	* http://www.gerrelt.nl/RaspberryPi/wordpress/tutorial-stand-alone-squeezebox-server-and-player-for-bbq/
* backup? (automatic when backup is hooked up to the pi)
* create our own image?
* issue apt upgrade in crontab?

