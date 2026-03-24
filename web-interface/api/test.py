#!/usr/bin/env python

import fnmatch
import os
import glob
'''        
dir = '/home/mark/Temp/Metallica/Metallica (Black Album)'
for drFileName in os.listdir(dir):
    if fnmatch.fnmatch(drFileName, 'dr14*.txt'):
        print(drFileName)
        break

'''

#collectionFolder = '/home/mark/Temp'
collectionFolder = '/media/mark/BACKUP/user/music/flac'

startLevel = collectionFolder.count(os.sep)
for (dir, dirs, files) in os.walk(collectionFolder):
    # print(dir)
    dirs.sort()
    level = dir.count(os.sep) - startLevel
    dirName = dir.split(os.path.sep)[-1]
    if level > 0:
        drFileFilter = os.path.join(dir, 'dr14*.txt')
        drFileList = list(glob.glob(drFileFilter))
        drValue = ''
        if len(drFileList) > 0:
            drFileName = drFileList[0] # In theory, there could be more than 1
            # print(' =>' + drFileName)
            
            try:
                drValue = os.popen('cat "' + drFileName + '" | grep "Official DR value:" | cut -c24-27 &> /dev/null').read().strip()
                if drValue != '':
                    drValue = drFileName + ' | DR' +  drValue
                    print(drValue)            
            except:
                pass    

                
                
                
