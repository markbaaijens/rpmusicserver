# rpmusicserver
Transform a Raspberry Pi in a music server with LMS (Squeezebox), Samba, transcoder, etc.

## Steps to turn a Pi into a music server:
* burn sd-kaart via burn-image script
* format usb-disk by format-usbdisk script (ext4, label = usbdisk)
* hookup hardisk to the pi
* reboot the clean system
* install ssh (standard in Raspbian?)
* remote installation with install-rp script via ssh
	* ssh root@remoteServer "bash -s" < install-rp
* reboot
