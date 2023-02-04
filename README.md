# Backup utility (`backup3.py`) for Windows cygwin, checking files time, md5 and logrotate.

The utility will compress files if md5 checksum is changed and copy it to destination folder. 
Rotate compressed files to keep desired number of copies in destination folder.

Backup utility use XZ utils for compressing. Pre-build `xz` binaries:
[https://tukaani.org/xz/](https://tukaani.org/xz/).
XZ Utils is under GNU GPL licenses.

Configure `backup3` editing `backup_cfg.yml` file:

```yaml
---
dest_dir: "/cygdrive/c/Users/<path to destination folder name>"
xz_path: "/cygdrive/c/Users/<path to xz binary>/xz.exe"
rotate_depth: 2  # how many copies to keep
```

Save list of files to backup with their paths to `backup.list` file:
```
c:\Users\<path1>\file1.odp
c:\Users\<path2>\file2.odp
```

Install Yaml dependencies:
```bash
pip3 install pyyaml
```

Run script:
```bash
$ ./backup3.py

Starting...
---  04. February
c:\Users\file1.odp
C:\Users\file2.odp
time: 02.02.202X 14:28:19 -> 04.02.202X 17:30:50
md5: b4ee450aee3cf2144exxxxxxxxxxx -> 85b853af71236c38f4521xxxxxxxxxxxxx
*** xz C:/Users/file2.odp

Done.
```