# rpmusicserver
Transform a Raspberry Pi in a music server with LMS (Squeezebox), Samba, transcoder, etc.

## Steps to turn a Pi into a music server:
* Download code:
  * `wget https://github.com/markbaaijens/rpmusicserver/archive/refs/heads/master.zip -O rpmusicserver.zip`
  * `unzip rpmusicserver.zip`
* Burn SD-card:
  * insert SD-card into your Linux PC
  * `sudo rpmusicserver-master/scripts/burn-image.sh`
* Format USB-drive for data (ext4, label = usbdata):
  * connect USB-drive to your Linux PC
  * `sudo rpmusicserver-master/scripts/format-usbdisk.sh`
* First boot:
  * make sure your Pi is powered off
  * insert SD-card into your Pi
  * connect USB-drive to the Pi
  * connect the Pi to your network with a network cable 
  * power up the Pi
  * check if Pi is running: `ping raspberrypi`
* Installation and configuration with install-rp script via ssh:
  * `rsync -r rpmusicserver-master/* pi@raspberrypi:/tmp/rpmusicserver`
	  * password = raspberry  
  * `ssh pi@raspberrypi "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`
	  * password = raspberry
  * system will be rebooted automatically after installation
* Test access:
  * `watch nmap raspberrypi`
    * wait until port 9002 appears
  * LMS: (browser) http://raspberrypi:9002
  * Samba: (file explorer) `smb://raspberrypi`  
* Engage:
  * copy music files to `smb://raspberrypi/Publiek/Muziek`
  * hookup a Squeezebox player to your network
  * enjoy!
