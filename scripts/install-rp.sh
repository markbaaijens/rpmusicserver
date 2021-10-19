#!/bin/bash

# (optional) update/upgrade
# (optional) hostname (= 'rp')
# (optional) users:
# - delete obsolete users like ubuntu, pi, etc.
# - create user 'user'(+ password)
# - change root-password
# packages
# - docker (by standard repo)
# - (later) transcoder
# - (later) dr14
# - (to be determined) extra tools like htop, net-tools, nano
# create folders (and rights)
# - /media/usbdata
# crontab
# - upgrade
# - (later) transcoder
# - (later) dr14tool
# fstab
#  LABEL=usbdata /media/usbdata ext4 auto,nofail 0 0
# (optional) squeezelite
# - config
# copy files
# - rc.local => /etc
#   - enable rc.local system
#   - make rc.local executable
# - lms-config => /etc/docker/lms
