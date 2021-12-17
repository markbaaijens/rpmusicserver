# RP Music Server
Transforms a Raspberry Pi in a music server with LMS (Logitech Media Server/Squeezebox), Samba, Tranmission, transcoder, etc.

## System requirements
* [minimum] Raspberry Pi 2 (B or B+), 1 GB
* [recommended] Raspberry Pi 4 B, 4 GB

## Steps to turn a Pi into a music server
* Install package(s) on your Linux PC:
  * `sudo apt-get install nmap`
    * enter your (personal) password of your PC  
* Download code:
  * `wget https://github.com/markbaaijens/rpmusicserver/archive/refs/heads/master.zip -O /tmp/rpmusicserver.zip`
  * `unzip -d /tmp -o /tmp/rpmusicserver.zip`
* Burn SD-card:
  * insert SD-card into your Linux PC
  * `sudo /tmp/rpmusicserver-master/scripts/burn-image.sh`
    * enter your (personal) password of your PC
* Format USB-drive for data:
  * connect USB-drive to your Linux PC
  * `sudo /tmp/rpmusicserver-master/scripts/format-usbdisk.sh`
    * enter your (personal) password of your PC
  * follow the instructions to format as a DATA-disk    
* First boot:
  * make sure your Pi is powered off
  * insert SD-card into your Pi
  * connect USB-drive to the Pi
  * connect the Pi to your network with a network cable 
  * power up the Pi
  * check if Pi is running: 
    * `watch nmap rpms`
    * wait until port 22 appears; exit with Ctrl-C
* Installation and configuration:
  * `rsync -r /tmp/rpmusicserver-master/* pi@rpms:/tmp/rpmusicserver`
	  * password = raspberry  
  * `ssh pi@rpms "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`
	  * password = raspberry
  * notes:
    * system will be rebooted automatically after installation
    * after reboot, password of user `pi` is changed to `rpms`
* Test access:
  * `watch nmap rpms`
    * wait until port 9002 appears; exit with Ctrl-C
  * LMS (browser): <a href="http://rpms:9002" target="_blank">rpms:9002</a>
  * Samba (file explorer): `smb://rpms`
  * Transmission (browser): <a href="http://rpms:9091" target="_blank">rpms:9091</a>
  * API: 
    * `curl rpms:5000`
    * <a href="http://rpms:5000" target="_blank">rpms:5000</a>
  * SSH: `ssh pi@rpms`
    * password: rpms
* Engage:
  * copy music files to `smb://rpms/Publiek/Muziek`
  * hookup a Squeezebox player to your network
  * install a Android App like <a href="https://play.google.com/store/apps/details?id=uk.org.ngo.squeezer" target="_blank">Squeezer</a>
  * enjoy!

### Update
Update your RPMS by SSH: 
* `ssh pi@rpms "sudo update-server"`

### Development
* To update RMPS from `develop` branch instead of `master`: 
  * `ssh pi@rpms "sudo bash -c 'echo \"develop\" > /media/usbdata/rpms/config/update-branch.txt'"`
* API-documentation: 
  * `curl rpms:5000/api/GetApiList`
  * <a href="http://rpms:5000/api/GetApiList" target="_blank">rpms:5000/api/GetApiList</a>

## Transcoder
For transcoding your lossless files (flac) into lossy ones (ogg or mp3), take the following steps:
* in your file explorer:
  * create a folder `flac` under `smb://rpms/Publiek/Muziek`
  * move your flac-files into that folder `flac`
* in <a href="http://rpms:9002" target="_blank">LMS</a> Server Settings, point music-folder to this location:
  * `/music/flac`
* change setting `sourcefolder`:
  * `curl rpms:5000/api/SetTranscoderSourceFolder -X post -H "Content-Type: application/json" -d '{"Value":"/media/usbdata/user/Publiek/Muziek/flac"}'`
* for transcoding to ogg
  * in your file explorer: 
    * create a folder `ogg` under `smb://rpms/Publiek/Muziek`
  * change setting `oggfolder`:
    * `curl rpms:5000/api/SetTranscoderOggFolder -X post -H "Content-Type: application/json" -d '{"Value":"/media/usbdata/user/Publiek/Muziek/ogg"}'`
* for transcoding to mp3
  * in your file explorer:
    * create a folder `mp3`under `smb://rpms/Publiek/Muziek`
  * change setting `mp3folder`:
    * `curl rpms:5000/api/SetTranscoderMp3Folder -X post -H "Content-Type: application/json" -d '{"Value":"/media/usbdata/user/Publiek/Muziek/mp3"}'`    
* from now on, every hour at 20 minutes, file transcoding will take place and lossy-files will automagically appear in the given lossy-folder!

### Notes
* Transcoding will be done by these default quality-levels: ogg = 1, mp3 = 128. Optionally, you can change these defaults:
  * for example, change `oggquality` to 3 (value = 1, 2, 3, 4, or 5):
     * `curl rpms:5000/api/SetTranscoderOggQuality -X post -H "Content-Type: application/json" -d '{"Value": 3}'`
  * for example, change `mp3bitrate` to 256 (value = 128, 256 or 384):
     * `curl rpms:5000/api/SetTranscoderMp3BitRate -X post -H "Content-Type: application/json" -d '{"Value": 256}'`     
* Trancoding simultaneously to ogg AND mp3 is possible; just set both `oggfolder` and `mp3folder`

## Backup
You can make a backup of all the data contained in your RPMS-server. This backup will be done to a dedicated backup-disk, connected to the Pi it self, a so called server-based backup.

* format a disk dedicated for RPMS-backups (one-time only):
  * connect your (empty) backup-disk to your PC
  * `wget https://github.com/markbaaijens/rpmusicserver/raw/master/scripts/format-usbdisk.sh -O /tmp/format-usbdisk.sh && chmod +x /tmp/format-usbdisk.sh && sudo /tmp/format-usbdisk.sh`
    * enter your (personal) password of the client-machine
  * follow the instructions to format as a BACKUP-disk
* engage the backup:
  * connect your backup-disk to the Pi
  * start the backup
    * `curl rpms:5000/api/DoBackupServer -X post`
  * watch progress
    * <a href="http://rpms:5000/api/GetBackupLog/4" target="_blank">rpms:5000/api/GetBackupLog/4</a>
    * refresh until log states: 'Backup ended'
  * see full backup-log
    * <a href="http://rpms:5000/api/GetBackupDetailsLog/0" target="_blank">rpms:5000/api/GetBackupDetailsLog/0</a>
  * disconnect backup-disk

### Off-line viewing backup-data
Backup-disk is formatted as ext4; for off-line viewing on your own PC, this format is natively supported on Linux, so it is plug-and-play. Windows however requires additional drivers. And worse, MacOS does NOT support ext4 (despite ext2 being open-source/open-standard).

### Disaster-recovery
B/c the backup-disk is an exact copy aka mirror of the data-disk and even of the same disk-type (ext4), you can simply swap them once the data-disk has been crashed. Just rename the label of the backup-disk from `usbbackup` to `usbdata`, connect the disk to the Pi and boot up. The backup-disk has been automagically changed into a data-disk by now and you can go on from the last backup that you made. Remember to make a backup to a new backup-disk immediately!
