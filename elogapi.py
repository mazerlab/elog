#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

# External API/interface for elog functions (ie, for pype). Provides:
#
#   getdb()
#     - get database handle
#   GetExper()
#     - get latest exper
#   GetNextExper(animal)
#     - get next exper for specified animal
#   AddDatafile(exper, animal, user, fname, filetype, date, crap, note, force)
#     - insert specified file into database
#

from tools import *

def getdb(**kwargs):
    """Open mysql database and return handle.

    This is for programs or tools that want to directly query or
    manipulate the database. You can pass keyword args to the
    Database constructor as follows:

    quiet (bool) - print debugging info to stderr
    host (str)   - hostname ('sql.mlab.yale.edu')
    db (str)     - database name ('mlabdata')
    user (str)   - database user ('mlab')
    passwd (str) - database password for specified ('mlab')

    Defaults will provide the same level of access you get running
    the elog program.
    """
    return Database(**kwargs)

def GetExper(animal):
    """Query database for most recent exper (eg, flea0204, merc0182 etc).
    """
    db = getdb()
    try:
        # get the last non-training exper for this animal from the database
        # by using LIKE for animal, this should handle prefixing correctly..
        rows = db.query("""SELECT exper FROM exper"""
                        """ WHERE animal LIKE '%s%%'"""
                        """ AND exper not like '%%0000'"""
                        """ ORDER BY exper DESC LIMIT 1""" %
                        (animal,))
        if rows is None:
            return None
    finally:
        db.close()

    if len(rows) == 0:
        return None
    else:
        return rows[0]['exper']

def GetNextExper(animal):
    e = GetExper(animal)
    if e is None:
        nextno = 1
    else:
        nextno = int(e[-4:]) + 1
    return "%s%04d" % (animal, nextno)
    

def AddDatafile(exper, animal, user, fname, filetype,
                date=None, crap=0, note='', force=0):
    """Insert DFILE record into database with the specified parameters.
    """

    if date is None:
        date = today()

    db = getdb()
    try:
        rows = db.query("""SELECT ID FROM dfile WHERE src='%s'""" %
                        fname)

        if len(rows) == 0:
            if db.query("""INSERT INTO dfile (date,exper,animal,"""
                        """ src,filetype,user,crap)"""
                        """ VALUES ('%s','%s','%s','%s',"""
                        """ '%s','%s',%d)""" %
                        (date, exper, animal, fname,
                         filetype, user, crap, )) is None:
                return (0, "db insert error: %s\n" % (fname,))
        elif force:
            if db.query("""REPLACE INTO dfile (ID,"""
                        """ date,exper,animal,src,filetype,"""
                        """ user,crap)"""
                        """ VALUES (%d,'%s','%s','%s','%s','%s','%s',%d)""" %
                        (rows[0]['ID'], date, exper, animal,
                         fname, filetype, user, crap,)) is None:
                return (0, "db replace error: %s\n" % (fname,))
        else:
            return (0, "skipped already duplicate file: %s" % fname)

        rows = db.query("""SELECT ID FROM exper"""
                        """ WHERE date='%s' AND exper='%s'""" %
                        (date, exper,))

        # insert a corresponding experiment, if it doesn't already exist..
        if len(rows) == 0:
            db.query("""INSERT INTO exper (exper, animal, date)"""
                     """ VALUES %s""" % ((exper, animal, date),))
        return (1, None)
    finally:
        db.close()

if __name__ == '__main__':
    pass
