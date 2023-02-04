#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Backup and check
    - checking files time, md5
    - log rotate
'''
import os
import shutil
import sys
import time
from subprocess import call

import yaml
from yaml.loader import SafeLoader

import f_backup

print("\nStarting... \n--- ", time.strftime("%A, %d. %B %Y %H:%M"))

dep = 5  # log rotate depth

with open("backup_cfg.yml", "r") as yml:
    DEST_DIRS = yaml.load(yml, Loader=SafeLoader)["dest_dirs"]  # config remote dirs

with open("backup.list", "r") as bk:
    BACKUP_FILES = bk.readlines()  # list of files to backup

file_dat = {}
for fn in BACKUP_FILES:

    fname = fn.strip()
    fl = os.path.basename(fname)
    file_dat[fl] = {}
    file_dat[fl]["path"] = os.path.dirname(fname)
    file_dat[fl]["utime"], file_dat[fl]["mtime"], file_dat[fl]["md5"] = f_backup.create_md5(fname)

print(file_dat, "\n")

result = ""
template = '''%s:
    path: %s
    utime: %s
    mtime: %s
    md5: %s
'''

def get_dir(dir_name):
    '''
    Get file names list for remote dir
    '''
    out = []
    flist = os.listdir(dir_name)  #;print(dir_name, flist)
    for each in flist:
        if not ".bak" in each[-4:]:
            out.append(dir_name + "/" + each)

    return out


w_dirs = {}
for dr in DEST_DIRS:
    if os.path.exists(dr):
        w_dirs[dr] = []
    else:
        print("\nDirectory %s not available:", dr)

#print("Working directories: ", w_dirs)
        
for dr in w_dirs:
    w_dirs[dr] = w_dirs[dr] + get_dir(dr)

print("Available files: ", w_dirs)



def check_files(dr, files_list):

    global result

    files_list.sort()
    for fn in files_list:

        fname = fn.strip()
        fl = os.path.basename(fname)  
        path = os.path.dirname(fname)

        # check mod time & md5
        if os.path.exists(fname):

            t, tm, h = f_backup.create_md5(fname)

            if fl in file_dat.keys():
                #print(fl)
                if ( file_dat[fl]["utime"] < round(t,2) ): # t - should be round 2
                    print("time:", file_dat[fl]["mtime"], "->", tm)

                if ( file_dat[fl]["md5"] != h ):
                    print("| %s | %s | -> | %s |" % (fl, file_dat[fl]["md5"], h))
                    f_backup.logrotate(fl, dep, dr)
                    f_backup.xz(fl, file_dat[fl]["path"], dr)
                else:
                    print("| %s | %s | == | %s |" % (fl, file_dat[fl]["md5"], h))

            else:
                f_backup.xz(fl, file_dat[fl]["path"], dr)

            result = result + template % (fl, path, t, tm, h)
        else:
            print("Error: %s - Not exist!" % fname)
            #sys.exit(0)

print("Check and copy files...")
for dr in w_dirs.keys():

    print(dr)
    for each in BACKUP_FILES:
        fname = each.strip()
        fl = os.path.basename(fname)  
        path = os.path.dirname(fname)

        remote_file = os.path.join(dr, fl)

        if not os.path.exists(remote_file):
            shutil.copy2(fname, dr)
            w_dirs[dr].append(remote_file)
            print("copied %s \n" % remote_file)
            

print("Available files: ", w_dirs)

print("Check md5sums...")            
for dr in w_dirs.keys():
    
    print(dr)
    check_files(dr, w_dirs[dr])


print(result)

print("Done.")


