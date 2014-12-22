#!/bin/bash
if [[ $EUID -ne 0 ]]; then
  echo "You must be a root user" 2>&1
  exit 1
fi

curdir=`pwd`

mkdir /mnt/home/seqware/ini
cp dkfz_ini.tar.gz /mnt/home/seqware/ini
cd /mnt/home/seqware/ini
tar xvzf dkfz_ini.tar.gz
cd $curdir
chown seqware:seqware -R /mnt/home/seqware/ini
cp runjob_dkfy.py /mnt/home/seqware/runjob.py
chmod +x /mnt/home/seqware/runjob.py
chown seqware:seqware /mnt/home/seqware/runjob.py

