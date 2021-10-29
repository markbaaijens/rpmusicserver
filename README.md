# rpmusicserver
Transform a Raspberry Pi in a music server with LMS (Squeezebox), Samba, transcoder, etc.

## Steps to turn a Pi into a music server:
* download all code 
  * `wget https://github.com/markbaaijens/rpmusicserver/archive/refs/heads/master.zip -O rpmusicserver.zip`
  * `unzip rpmusicserver.zip`
* burn sd-card:
  * `sudo rpmusicserver-master/scripts/burn-image.sh`
* format usb-disk (ext4, label = usbdisk)
  * `sudo rpmusicserver-master/scripts/format-usbdisk.sh`
* hookup harddisk to the Pi
* reboot the clean system
* check if Pi is running
  * `ping raspberrypi`
* remote installation with install-rp script via ssh
  * `rsync -r ./* pi@raspberrypi:/tmp/rpmusicserver`
  * `ssh pi@raspberrypi "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`
	* password = raspberry
* system will be rebooted automatically after installation
* test access:
  * Samba: (file explorer) `smb://raspberrypi`
  * LMS: (browser) http://raspberrypi:9002
  * Transmission: (browser) http://raspberrypi:9091

