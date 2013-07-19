#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
import os
import string
import time
import types
import atexit


import MySQLdb
from Tkinter import *
import tkFont
import tkMessageBox
import Pmw_1_3_2 as Pmw

# from keyboard import keyboard

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

def ins_time(event):
    """Insert current timestamp into text widget.
    """
    event.widget.insert(INSERT, time.strftime('%H%Mh: '))

def die(tk):
    """Immediate quit w/o save!
    """
    tk.destroy()
    sys.exit(0)

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

def cachestate(animal=None, date=None):
    if animal or date:
        f = open(os.getenv('HOME')+'/.elogrc', 'w')
        f.write('%s\n' % animal)
        f.write('%s\n' % date)
        f.close()
    else:
        try:
            i = open(os.getenv('HOME')+'/.elogrc', 'r').readlines()
            return (i[0][:-1], i[1][:-1])
        except IOError:
            return (None, None)

def today():
    import datetime
    date = sdate("%s" % datetime.datetime(1,1,1).today())
    return date

class Msg:
    w = None
    def __init__(self, status=None, window=None):
        if window:
            Msg.w = window
        elif Msg.w:
            if status is None:
                Msg.w['text'] = ''
            else:
                Msg.w['text'] = status
                Msg.w.after(5000, lambda : Msg(None))


def raisetab(pagename, notebook):
    for k in notebook.pagenames():
        notebook.tab(k)['bg'] = '#808080'
        notebook.tab(k)['fg'] = '#b0b0b0'
    notebook.tab(pagename)['bg'] = '#ffffff'
    notebook.tab(pagename)['fg'] = '#000000'

def _env(var, default=None):
    import os
    try:
        return os.environ[var]
    except KeyError:
        return default

class Database(object):
    # Singleton object -- only one of these really exists!
    # default params (env vars override these!)
    _HOST   = 'sql.mlab.yale.edu'
    _DB = 'mlabdata'
    _USER   = 'mlab'
    _PASSWD = 'mlab'

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
            cls._init = 1
        else:
            cls._init = 0
        return cls._instance

    def __init__(self, host=None, db=None, user=None, passwd=None):
        if not Database._init: return

        if host is None:
            self.host = _env('ELOG_HOST', Database._HOST)
        if db is None:
            self.db = _env('ELOG_DB', Database._DB)
        if user is None:
            self.user = _env('ELOG_USER', Database._USER)
        if passwd is None:
            self.passwd = _env('ELOG_PASSWD', Database._PASSWD)

        self.connect()

    def connect(self):
        try:
            self.connection = MySQLdb.connect(self.host,
                                              self.user, self.passwd, self.db)
            self.cursor = self.connection.cursor()
            atexit.register(self._atexit)
        except MySQLdb.OperationalError as (errno, errstr):
            sys.stderr.write("Can't connect to: %s@%s\n" % (db, host,))
            sys.stderr.write('Error: %s\n' % errstr)
            self.connection = None

    def flush(self):
        self.connection.commit()

    def close(self):
        # Other instances may be floating around, so commit changes
        # and leave real close for the atexit method below.
        #
        # By keeping close() method, this allows flushing queries out
        # to the database, but ensures that the one live connection
        # is maintained until the process exits. Best I can do..
        self.flush()

    def _atexit(self):
        # this should only be called "atexit"
        if self.connection:
            self.flush()
            self.connection.close()
            self.connection = None
            self.cursor = None

    def query(self, cmd, *args):
        try:
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
            sys.stderr.write('SQL ERROR #%d: %s\nQUERY=<%s>\n' %
                             (number, msg, cmd))
            return None

def popup(w):
    w.winfo_toplevel().deiconify()
    w.winfo_toplevel().lift()

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

def ask(master, prompt, default):
    w = Pmw.PromptDialog(master,
                         title='Enter value',
                         label_text=prompt,
                         entryfield_labelpos = 'w',
                         defaultbutton = 0,
                         buttons = ('Ok', 'Cancel'))
    w.setvalue(default)

    x, y = master.winfo_pointerxy()   # -1 if off screen
    x = max(1, x - (w.winfo_width() / 2) - 10)
    y = max(1, y - (w.winfo_height() / 2) - 10)

    if w.activate(geometry='+%d+%d' % (x,y)) == 'Ok':
        response = w.getvalue()
        w.destroy()
        return response
    else:
        return None

def warn(master, mesg, buttons=("Dismiss",)):
    """
    Simple warning message dialog box
    """
    x, y = master.winfo_pointerxy()   # -1 if off screen
    w = Pmw.MessageDialog(master,
                          iconpos = 'w',
                          icon_bitmap = 'warning',
                          title='Warning',
                          buttons=buttons,
                          defaultbutton=0,
                          message_text=mesg)
    x = max(1, x - (w.winfo_width() / 2) - 10)
    y = max(1, y - (w.winfo_height() / 2) - 10)
    return w.activate(geometry='+%d+%d' % (x,y))

def choose(master, mesg, options):
    """
    Simple warning message dialog box
    """
    x, y = master.winfo_pointerxy()   # -1 if off screen
    w = Pmw.MessageDialog(master,
                          iconpos = 'w',
                          title='Select one',
                          buttons=options,
                          defaultbutton=0,
                          buttonboxpos = 'e',
                          message_text=mesg)
    x = max(1, x - (w.winfo_width() / 2) - 10)
    y = max(1, y - (w.winfo_height() / 2) - 10)
    r = w.activate(geometry='+%d+%d' % (x,y))
    return r


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
    sys.path = sys.path + [dir+'/lib']

def insert_dfile(db, fname, force=None):
    """Try to insert record for existing datafile into the database.
    """
    from pypedata import PypeFile

    # ugly hack -- hard coded mapping between file prefixes
    # and animal names ... this should really be in the database
    # somewhere..
    animals = {
        'pid': 'picard',
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

    rows = db.query("""SELECT dfileID FROM dfile WHERE src='%s'""" % fname)

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
                    (fieldlist, rows[0]['dfileID'],
                     date, exper, animal, fname, taskname,
                     user, crap, preferred,)) is None:
            sys.stderr.write("db replace error: %s\n" % (fname,))
    else:
        sys.stderr.write("skipped duplicate: %s\n" % fname)
        return 1

    rows = db.query("""SELECT experID FROM exper"""
                    """ WHERE date='%s' AND exper='%s'""" % (date, exper,))

    # insert a corresponding experiment, if it doesn't already exist..
    if len(rows) == 0:
        if db.query("""INSERT INTO exper (exper, animal, date)"""
                    """VALUES %s""" % ((exper, animal, date), )) is None:
            sys.stderr.write('error db insert\n')

    return 1

def textwarn(title, message):
	from Dialog import DIALOG_ICON

	dialog = Toplevel()
	dialog.title(title)
	dialog.iconname('info')
	dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

	parent = dialog._nametowidget(dialog.winfo_parent())

	f = Frame(dialog)
	f.pack(expand=1, fill=BOTH)

    text = Pmw.ScrolledText(f,
                            text_height=min(message.count('\n'), 30),
                            text_width=75,
                            labelpos='w')
    text.setvalue(message)
    text.component('text').see("0.0")
	text.pack(expand=1, fill=BOTH)

    b = Button(dialog, text='close', command=dialog.destroy)
	b.pack(expand=0, fill=X)

	b.bind('<Return>', lambda e, w=dialog: w.destroy())
	b.bind('<Escape>', lambda e, w=dialog: w.destroy())
	b.focus_set()

	# position the widget under the mouse
	#undermouse(dialog)

    return dialog


class ToolTip(object):
	def __init__(self, widget):
		self.widget = widget
		self.tipwindow = None
		self.id = None
		self.x = self.y = 0

	def showtip(self, text):
		"Display text in tooltip window"
		self.text = text
		if self.tipwindow or not self.text:
			return
		x, y, cx, cy = self.widget.bbox("insert")
		x = x + self.widget.winfo_rootx() + 27
		y = y + cy + self.widget.winfo_rooty() +27
		self.tipwindow = tw = Toplevel(self.widget)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))
		label = Label(tw, text=self.text, justify=LEFT,
					  background="#ffffe0", relief=SOLID, borderwidth=1,
					  font=("tahoma", "8", "normal"))
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()

def createToolTip(widget, text):
	toolTip = ToolTip(widget)
	def enter(event):
		toolTip.showtip(text)
	def leave(event):
		toolTip.hidetip()
	widget.bind('<Enter>', enter)
	widget.bind('<Leave>', leave)
