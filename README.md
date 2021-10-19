# rpmusicserver
Transform a Raspberry Pi in a music server with LMS (Squeezebox), Samba, transcoder, etc.

## Steps to turn a Pi into a music server:
* download all code (wget)
* burn sd-card by burn-image script
* format usb-disk by format-usbdisk script (ext4, label = usbdisk)
* hookup hardisk to the pi
* reboot the clean system
* remote installation with install-rp script via ssh
	* ssh pi@raspberrypi "bash -s" < install-rp.sh
	* password: raspberry
* (ssh) execute /etc/rc.local to monitor installation proces
* (ssh) reboot
