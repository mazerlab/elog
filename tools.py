#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
import os
import string
import time

import MySQLdb

BOOL = 'bool'
TEXT = 'text'
INTEGER = 'integer'
REAL = 'real'

def gethost():
    import socket
    return socket.gethostname()

def getuser():
    import getpass
    return getpass.getuser()

def find_animals(db):
    """Get a list of all animals in database
    """
    rows = db.query("""SELECT animal FROM session WHERE 1""")
    return unique([row['animal'] for row in rows])

def find_expers(db, exper):
    """Get a list of all dates with specified exper
    """
    rows = db.query("""SELECT exper,date,animal FROM exper"""
                    """ WHERE exper='%s' ORDER BY date""" %
                    exper)
    if len(rows) == 0:
        sys.stderr.write("Can't find exper='%s'\n" % exper)
        return None, None
    if len(rows) > 1:
        sys.stderr.write("%d date(s) have exper='%s'\n" % (len(rows), exper))
        return None, None
    return rows[0]['animal'], '%s'%rows[0]['date']


def find_dfiles(db, animal, date, exper=None):
    if exper:
        rows = db.query("""SELECT src FROM dfile"""
                        """ WHERE animal='%s' AND date='%s' AND exper='%s'""" %
                        (animal, date, exper,))
    else:
        rows = db.query("""SELECT src FROM dfile"""
                        """ WHERE animal='%s' AND date='%s'"""
                        % (animal, date,))

    flist = {}
    for row in rows:
        flist[os.path.basename(row['src'])] = row['src']
    return flist

def today():
    import datetime
    date = sdate("%s" % datetime.datetime(1,1,1).today())
    return date

def _env(var, default=None):
    import os
    try:
        return os.environ[var]
    except KeyError:
        return default

class Database(object):
    def __init__(self, host=None, port=None, db=None,
                 user=None, passwd=None, quiet=True):
        import dbsettings
        
        if host is None:
            self.host = _env('ELOG_HOST', dbsettings.HOST)
        if port is None:
            self.port = int(_env('ELOG_PORT', dbsettings.PORT))
        if db is None:
            self.db = _env('ELOG_DB', dbsettings.DB)
        if user is None:
            self.user = _env('ELOG_USER', dbsettings.USER)
        if passwd is None:
            self.passwd = _env('ELOG_PASS', dbsettings.PASS)
            
        self.quiet = quiet
        
        self.connect()

    def __del__(self):
        self.close()

    def connect(self):
        try:
            self.connection = MySQLdb.connect(host=self.host,
                                              port=self.port,
                                              user=self.user,
                                              passwd=self.passwd,
                                              db=self.db)
            self.cursor = self.connection.cursor()
        except MySQLdb.OperationalError as (errno, errstr):
            sys.stderr.write("Can't connect to: '%s' %s@%s:%d\n" % \
                             (self.db, self.user, self.host, self.port,))
            sys.stderr.write('Error: %s\n' % errstr)
            self.connection = None
            sys.exit(1)

    def flush(self):
        self.connection.commit()

    def close(self):
        if self.connection:
            self.flush()
            self.connection.close()
            self.connection = None
            self.cursor = None

    def query(self, cmd, *args):
        try:
            if not self.quiet:
                sys.stderr.write('cmd: <%s>\n' % cmd)
            result = []
            self.cursor.execute(cmd, *args)
            fields = self.cursor.description
            for row in self.cursor.fetchall():
                dict = {}
                for fnum in range(len(fields)):
                    if row[fnum] is None:
                        # value is NULL, use empty string to represent..
                        dict[fields[fnum][0]] = ''
                    else:
                        dict[fields[fnum][0]] = row[fnum]
                result.append(dict)
            return result
        except MySQLdb.Error, e:
            (number, msg) = e.args
            sys.stderr.write('SQL ERROR #%d: <%s>\nQUERY=<%s>\n' %
                             (number, msg, cmd))
            return None

    def dquery(self, readonly, cmd, *args):
        """
        For destructive queries: only allows if readonly is False
        """
        if readonly:
            sys.stderr.write("RO, skipped: <%s...>\n" % cmd[:45]);
            return
        else:
            return self.query(cmd, *args)

def isarg(arg, option):
    if arg[0:len(option)] == option:
        return 1
    return 0

def yn(i):
    if i > 0:
        return 'YES'
    if i < 0:
        return 'n/d'
    return 'NO'

def unique(seq):
    """
    Find unique entries in a sequence.
    """
    d = {}
    for s in seq:
        d[s] = 1
    return d.keys()

def sdate(datestr):
    # in old versions of python datetime objects include the
    # time in their __repr__ return.. here we just trim out the
    # date part...
    return ("%s"%datestr)[0:10]


def unlink_exper(link):
    """Unpack link of form <elog:exper=DATE/EXPER> and return DATE, EXPER
    """
    date, exper = link[1:-1].split('=')[1].split('/')
    return date, exper

def unlink_dfile(link):
    """Unpack link of form <elog:file=DATE/FNAME> and return DATE, FNAME
    """
    date, fname = link[1:-1].split('=')[1].split('/')
    return date, fname

def find_pype():
    """Find pype installation and pype library dir to python search path.
    """
    dir = os.popen('pype --dir', 'r').readline()[:-1]
    sys.path = sys.path + [dir+'/pype']

def insert_dfile(db, fname, force=None):
    """Try to insert record for existing datafile into the database.
    """
    from pypedata import PypeFile

    # ugly hack -- hard coded mapping between file prefixes
    # and animal names ... this should really be in the database
    # somewhere..
    animals = {
        'pic': 'picard',
        'merc': 'mercutio',
        }

    try:
        pf = PypeFile(fname, quiet=1)
    except IOError:
        sys.stderr.write("can't open: %s\n" % fname)
        return 0

    rec = pf.nth(0)
    pf.close()

    # strip .gz, if it's there to get original filename for database
    if fname[-3:] == ".gz":
        fname = fname[:-3]
    base = os.path.basename(fname)
    (exper, taskname, seqnum) = string.split(base, '.')
    animal = exper[:-4]
    try:
        animal = animals[animal]
    except KeyError:
        pass

    try:
        date = time.strptime(string.split(rec.trialtime)[0], '%d-%b-%Y')
        date = '%04d-%02d-%02d' % date[:3]
    except:
        # /path/to/data/storage/DATE/AnimalNNNN.TASK.NNN
        date = os.path.basename(os.path.dirname(fname))

    try:
        user=rec.params['owner']
    except:
        user=''

    rows = db.query("""SELECT ID FROM dfile WHERE src='%s'""" % fname)

    crap = 0
    preferred = 0

    fieldlist = '(date, exper, animal, src, filetype, user, crap, preferred)'

    if len(rows) == 0:
        if db.query("""INSERT INTO dfile (%s)"""
                    """ VALUES ('%s','%s','%s','%s','%s','%s',%d,%d)""" %
                     (fieldlist, date, exper, animal, fname, taskname,
                      user, crap, preferred,)) is None:
            sys.stderr.write("db insert error: %s" % (fname,))
    elif force:
        if db.query("""REPLACE INTO dfile (%s)"""
                    """ VALUES (%d,'%s','%s','%s','%s','%s','%s',%d,%d)""" %
                    (fieldlist, rows[0]['ID'],
                     date, exper, animal, fname, taskname,
                     user, crap, preferred,)) is None:
            sys.stderr.write("db replace error: %s\n" % (fname,))
    else:
        sys.stderr.write("skipped dup: %s\n" % fname)
        return 1

    rows = db.query("""SELECT ID FROM exper"""
                    """ WHERE date='%s' AND exper='%s'""" % (date, exper,))

    # insert a corresponding experiment, if it doesn't already exist..
    if len(rows) == 0:
        if db.query("""INSERT INTO exper (exper, animal, date)"""
                    """VALUES %s""" % ((exper, animal, date), )) is None:
            sys.stderr.write('error db insert\n')

    return 1

