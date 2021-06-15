#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Backup 'bicycle' for Windows
    - using cygwin
    - checking files time, md5
    - log rotate
2014 Dec
A. Maslennikov
'''
import os
import shutil
import sys
import time
import hashlib
import yaml
from subprocess import call
import time

d = 5 # log rotate depth
dest_dir = yaml.load(open("backup_cfg.yml"))["dest_dir"] # config remote dir
print("\nStarting... \n--- ", time.strftime("%A, %d. %B %Y %H:%M"))

states = "backup.yml" # store files hashes and modify times
bk = open(states)
file_dat = yaml.load(bk) 
bk.close()

f = open("backup.list", "r") # list of files to backup

def logrotate(file, depth):
    '''
    rename remote files to .old
    '''
    # create old version
    old = ".old"
    remote_file = dest_dir + file + ".xz"
    
    for i in range(depth, 1, -1):
        old_remote_file1 = remote_file + old + str(i-1)
        old_remote_file2 = remote_file + old + str(i)

        if os.path.exists(old_remote_file2):
            os.remove(old_remote_file2)

        if os.path.exists(old_remote_file1):
            os.rename(old_remote_file1, old_remote_file2)

    old_remote_file = remote_file + old + str(1)

    if os.path.exists(remote_file):
        os.rename(remote_file, old_remote_file)

def xz(lfile, local_dir):
    '''
    xz and copy new files
    '''
    lfile = lfile.replace("\\", "/")
    local_file = os.path.join(local_dir, lfile)
    xz_local_file = local_file + ".xz"

    # xz
    call(["c:/Doc/bin/xz/xz.exe", "-kf", local_file])
    #call(["c:\\Program Files\\7-Zip\\7z.exe", "a", "-bb0", xz_local_file, local_file])
   
    # cp new version 
    shutil.copy2(xz_local_file, dest_dir)
    print("*** xz %s \n" % lfile)

result = ""
template = '''%s:
    path: %s
    utime: %s
    mtime: %s
    md5: %s
'''
for fn in f:

    fname = fn.strip()
    fl = os.path.basename(fname)  
    path = os.path.dirname(fname)   # windows path

    # check mod time & md5
    if os.path.exists(fname):
        t = os.path.getmtime(fname)
        tm = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(t)) 

        # md5sum
        newfile = open(fname, "rb")
        content = newfile.read()
        newfile.close()
        m = hashlib.md5()
        m.update(content)
        h = m.hexdigest()

        if fl in file_dat.keys():
            print(fl)

            if round(file_dat[fl]["utime"],2) < round(t,2): # t - should be round 2
                print("time:", file_dat[fl]["mtime"], "->", tm)
                #print file_dat[fl]["utime"], type(file_dat[fl]["utime"]) 

            if file_dat[fl]["md5"] != h:
                print("md5: %s -> %s" % (file_dat[fl]["md5"], h))
                logrotate(fl, d)
                xz(fl, path)
            #else:
                #print "ok!\n"
        else:
            xz(fl, path)

        result = result + template % (fl, path, t, tm, h)

    else:
        print("Error: %s - Not exist!" % fname)
        #sys.exit(0)

#print result
dat = open(states, "w")
dat.writelines(result)
dat.close()

f.close()
print("Done.")
#input()
