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

CFG = yaml.load(open("backup_cfg.yml"), Loader=yaml.SafeLoader)
DEST_DIR = CFG["dest_dir"]  # config remote dir
XZ_PATH = CFG["xz_path"]
DEP = CFG["rotate_depth"]  # log rotate depth

print("\nStarting... \n--- ", time.strftime("%A, %d. %B %Y %H:%M"))

states = "backup.yml"  # store files hashes and modify times
bk = open(states)
file_dat = yaml.load(bk, Loader=yaml.SafeLoader)
bk.close()

f = open("backup.list", "r")  # list of files to backup

def logrotate(fl, depth):
    '''
    rename and rotate remote files to .old
    '''
    # create old version
    old = ".old"
    xz_file = fl + ".xz"
    remote_file = os.path.join(DEST_DIR, xz_file)

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

    #print("Rotate %s with %s" % (remote_file, old_remote_file))


def xz(lfile, local_dir):
    '''
    xz and copy new files
    '''
    local_file = os.path.join(local_dir, lfile)
    xz_local_file = local_file + ".xz"

    # xz
    call([XZ_PATH, "-kf", local_file])
    #call(["c:\\Program Files\\7-Zip\\7z.exe", "a", "-bb0", xz_local_file, local_file])

    # cp new version 
    shutil.copy2(xz_local_file, DEST_DIR)
    print("*** xz %s \n" % local_file)


result = ""
template = '''%s:
    path: %s
    utime: %s
    mtime: %s
    md5: %s
'''

for full_name in f:

    full_name = full_name.strip()
    lname = full_name.replace("\\", "/")  # change windows path
    fname = os.path.basename(lname)
    path = os.path.dirname(lname)
    #print("name %s, path %s: " % (fl, path))

    # check mod time & md5
    if os.path.exists(lname):
        t = os.path.getmtime(lname)
        tm = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(t))

        # md5sum
        newfile = open(lname, "rb")
        content = newfile.read()
        newfile.close()
        m = hashlib.md5()
        m.update(content)
        h = m.hexdigest()

        try:
            fl_keys = file_dat.keys()
        except:
            fl_keys = {}

        if full_name in fl_keys:
            print(full_name)

            if round(file_dat[full_name]["utime"],2) < round(t,2):  # t - should be round 2
                print("time:", file_dat[full_name]["mtime"], "->", tm)
                #print file_dat[fl]["utime"], type(file_dat[fl]["utime"]) 

            if file_dat[full_name]["md5"] != h:
                print("md5: %s -> %s" % (file_dat[full_name]["md5"], h))
                logrotate(fname, DEP)
                xz(fname, path)
            #else:
                #print "ok!\n"
        else:
            xz(fname, path)

        result = result + template % (full_name, path, t, tm, h)

    else:
        print("Error: %s - Not exist!" % full_name)
        #sys.exit(0)

dat = open(states, "w")
dat.writelines(result)
dat.close()

f.close()
print("Done.")
#input()
