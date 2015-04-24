#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

# update note field for datafiles to include attachments

import sys
import os
import string
import types
import datetime, time


try:
    elogpath = os.popen('elog -dir 2>/dev/null').read()[:-1]
except:
    elogpath = None
    
if elogpath is None:
	sys.stderr.write("Can't find elog executable/path\n")
	sys.exit(1)
else:
    elogpath = elogpath + '/lib/elog'
	sys.path.append(elogpath)
	from elogapi import getdb

def getuser():
    import getpass
    return getpass.getuser()

def today(n=0):
    import datetime
    return (datetime.datetime.now() -
            datetime.timedelta(days=n)).strftime("%Y-%m-%d")


if __name__ == '__main__':
    db = getdb()

    fname = sys.argv[1]
    title = sys.argv[2]
    note = sys.stdin.read()
    im = open(fname, 'r').read().encode('base64')
    ftype = fname.split('.')[-1]

    db.query("""INSERT INTO attachment """
             """ (title, date, user, note, type, data) VALUES """
             """ ('%s', '%s', '%s', '%s', '%s', '%s') """ %
             (title, today(), getuser(), note, ftype, im))

