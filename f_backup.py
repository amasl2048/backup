#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import shutil
from subprocess import call

import hashlib


def create_md5(f_name):

    # check mod time & md5
    if (os.path.exists(f_name)):
        t = os.path.getmtime(f_name)
        tm = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(t)) 

        # md5sum
        newfile = open(f_name, "rb")
        content = newfile.read()
        newfile.close()
        
        m = hashlib.md5()
        m.update(content)
        h = m.hexdigest()

    return t, tm, h


def logrotate(fl_name, depth, dest_dir):
    '''
    rename remote files with .x.bak
    '''
    # create old version
    old = "bak"
    remote_file = dest_dir + "/" + fl_name  #+ ".xz"
    
    for i in range(depth, 1, -1):
        old_remote_file1 = "%s.%s.%s" % (remote_file, str(i-1), old)
        old_remote_file2 = "%s.%s.%s" % (remote_file, str(i), old)
        if os.path.exists(old_remote_file2):
            os.remove(old_remote_file2)
        if os.path.exists(old_remote_file1):
            os.rename(old_remote_file1, old_remote_file2)

    old_remote_file = "%s.%s.%s" % (remote_file, str(1), old)
    os.rename(remote_file, old_remote_file)


def xz(fl_name, local_dir, dest_dir):
    '''
    xz and copy new files
    '''
    local_file = os.path.join(local_dir, fl_name)

    # xz
    #call(["xz", "-kf", local_file])
   
    # cp new version
    #xz_local_file = local_file# + ".xz"
    shutil.copy2(local_file, dest_dir)
    print("copied %s \n" % fl_name)
