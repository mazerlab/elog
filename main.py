#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

# elog database has 4 tables:
#   - SESSION: main daily record (one per day)
#     * EXPER: one per experiment or recording site (many per SESSION)
#       + UNIT: one per isolated unit (many per EXPER)
#       + DFILE: one per datafile/run (many per EXPER)

#
#
# Wed Mar 26 17:43:19 2014 mazer -- TODO for attachments:
#  - for in-text attachments, still need to figure out a way to
#    go through and find attachments w/o links...
#  - need to add support for these in dump files
#

import string
import sys
import os
import types
import datetime
import time
import re
import numpy as np

#from keyboard import keyboard

if os.environ.has_key('DISPLAY'):
    from Tkinter import *
    import PmwBundle as Pmw
    import tkdialogs

from tools import *
from guitools import *
import dumphtml
import layout

from elogapi import getdb

READ_ONLY = False
MINDTB = 10.0
logwin = None

def ins_attachment(event, w):
    """Insert current timestamp into text widget.
    """
    id = attach(w, im=None, title='')
    txt = event.widget
    tag = '<elog:attach=%d>' % id
    txt.mark_set('tmp', INSERT)
    txt.mark_gravity('tmp', LEFT)
    txt.insert(INSERT, tag)
    txt.tag_add('attachlink', txt.index('tmp'), INSERT)
    txt.mark_unset('tmp')

    b = Button(txt)
    b.im = pil_getattach(id, (128,128))
    b.config(image=b.im,
             command=lambda m=w,id=id: \
             AttachmentViewer(m,id))
    createToolTip(b, 'attachment #%d' % id)
    txt.window_create(INSERT, window=b, padx=10)
    

def attach(tk, im=None, title='no title', note=''):
    """Use imagemagick 'import' command to grab a screen capture
    of a window or region as JPEG image and store in string
    """

    db = getdb()

    if im is None:
        im = os.popen('import jpeg:-', 'r').read().encode('base64')

    if db.dquery(READ_ONLY,
                """INSERT INTO attachment"""
                """ (type,user,date,title,note,data)"""
                """ VALUES ('%s','%s','%s','%s','%s','%s')""" % \
                    ('jpeg', getuser(), today(), title, note, im,)) is None:
        sys.stderr.write("elog: db insert attachment error\n")
        return
    rows = db.query("""SELECT ID FROM attachment"""
                    """ ORDER BY ID DESC LIMIT 1""")
    id = rows[0]['ID']
    if tk:
        w = AttachmentViewer(tk, id, title=title)
    return id

def isdel(date, exper):
    """Check to see if 'exper' has been marked as deleted.
    """
    rows = Database().query("""SELECT deleted FROM exper"""
                         """ WHERE date='%s' AND exper='%s'"""
                         % (date, exper,))
    return rows[0]['deleted']

def all_cloudtags():
    """Get list of all tags from database
    """
    tags = {}
    for table in ('attachment', 'dfile', 'exper', 'session', 'unit'):
        rows = Database().query("""SELECT tags FROM %s WHERE 1""" % (table,))
        for row in rows:
            for tag in row['tags'].split(','):
                if len(tag) > 0:
                    try:
                        tags[tag] += 1
                    except KeyError:
                        tags[tag] = 1
    return tags.keys()

def cloudtag_select(parent):
    d = Pmw.ComboBoxDialog(parent,
                           title='Select tag',
                           buttons = ('Ok', 'Cancel'),
                           scrolledlist_items = all_cloudtags())
    if d.activate() == 'Ok':
        return d.get()
    else:
        return None

def pil_getattach(id, size=None):
    import PIL.Image
    import StringIO
    import PIL.ImageTk

    db = getdb()

    rows = db.query("""SELECT * FROM attachment"""
                    """ WHERE ID=%d""" % (id,))
    if len(rows) == 0:
        return None
    imstr = rows[0]['data'].decode('base64')
    p = PIL.Image.open(StringIO.StringIO(imstr))
    if size:
        p.thumbnail(size)
    im = PIL.ImageTk.PhotoImage(p)
    return im

class AttachmentViewer(Toplevel):
    attachmentList = {}

    def __init__(self, master, id, title=None, note=None, **kw):
        self.id = id

        self.im, self.rows = self.getattach()
        if title:
            self.rows['title'] = title
        if note:
            self.rows['note'] = note

        Toplevel.__init__(self, master, **kw)
        self.winfo_toplevel().title('Attachment#%d' % self.id)

        f = Frame(self)
        f.pack(expand=1, fill=BOTH)

        bb = Frame(f)
        bb.pack(expand=1, fill=X)

        Button(bb, text='save', \
               command=self.save).pack(side=LEFT, expand=0)
        Button(bb, text='delete', \
               command=self.db_delete).pack(side=LEFT, expand=0)

        self.rv = RecordView(f, layout.ATTACHMENT_FIELDS, False)
        self.rv.pack(side=TOP, expand=1, fill=BOTH)
        self.rv.setall(self.rows)

        Label(f, image=self.im, \
              relief=SUNKEN, borderwidth=3).pack(side=BOTTOM, padx=10, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.close)

        AttachmentViewer.attachmentList[self.rows['ID']] = self

    def getattach(self):
        import PIL.Image
        import StringIO
        import PIL.ImageTk
        db = getdb()

        rows = db.query("""SELECT * FROM attachment"""
                        """ WHERE ID=%d""" % (self.id,))
        imstr = rows[0]['data'].decode('base64')
        im = PIL.ImageTk.PhotoImage(PIL.Image.open(StringIO.StringIO(imstr)))
        return im, rows[0]

    def db_delete(self):
        i = warn(self, "\nReally delete attachment?\n",
                 ("Ok", "Cancel"))
        if i > 0:
            return

        # delete actual attachment
        db = getdb()
        db.dquery(READ_ONLY,
                  """DELETE FROM attachment WHERE ID=%d""" %
                      (self.id,))

        # note: notes that actually refer to the attachement will be
        # deleted the next time they are displayed..
        
        self.destroy()

    def save(self):
        self.rv.save(table='attachment',
                     key=('ID', self.id))

    def close(self):
        self.save()
        self.destroy()
        del AttachmentViewer.attachmentList[self.rows['ID']]


def clipcopy(widget, str):
    """Copy string to clipboard for standard pasting
    """
    widget.clipboard_clear()
    widget.clipboard_append(str)

class Checkbutton2(Frame):
    """Modified checkbutton widget idea from:
    http://mail.python.org/pipermail/tkinter-discuss/2011-January/002752.html
    """
    def __init__(self, master=None, **kw):

        if kw.has_key('text'):
            text = kw['text']
            del(kw['text'])
        else:
            text = ''

        if kw.has_key('state'):
            state = kw['state']
            del(kw['state'])
        else:
            state = None

        Frame.__init__(self, master, **kw)

        self.var = IntVar()
        self.label = Label(self, text=text)
        self.label.pack(side=LEFT, fill=X)
        self.checkbutton = Checkbutton(self, variable=self.var)
        if not state is None:
            self.checkbutton.configure(state=state)
        self.checkbutton.pack(side=RIGHT)

    def setvalue(self, value):
        if value == '':
            value = 0
        self.var.set(value)

    def getvalue(self):
        v = self.var.get()
        return v

class RecordView(Frame):
    def __init__(self, master, fields, allowattach, **kwargs):
        Frame.__init__(self, master, **kwargs)

        self._entries = {}
        self._validators = {}
        self._converters = {}
        self._children = []
        self._children_info = {}

        self.frame1 = Frame(self)
        self.frame1.pack(expand=0, fill=X, side=TOP)
        self.frame2 = Frame(self)
        self.frame2.pack(expand=1, fill=BOTH, side=BOTTOM)

        elist = []
        elist_by_col = {}
        for fd in fields:
            (fieldname, validator, converter, state, sz, pos, callback) = fd

            if '>' in fieldname:
                # allow for a different sql name and label: 'sqlfield>..label..'
                sqlname, fieldname = fieldname.split('>')
            else:
                s = fieldname.split()
                if len(s) > 1:
                    sqlname = s[0]
                else:
                    sqlname = fieldname

            if sz is None:
                # create widget, but don't show it..
                e = Pmw.EntryField(self.frame1, labelpos='w',
                                   label_text=fieldname)
                e.component('entry')['state'] = state
            else:
                (row, col, cspan) = pos
                if not elist_by_col.has_key(col):
                    elist_by_col[col] = []

                fbox = Frame(self.frame1, relief=GROOVE, borderwidth=2)
                if type(validator) == types.TupleType:
                    # this doesn't quite work yet!
                    e = Pmw.ComboBox(fbox, labelpos='w',
                                     label_text=fieldname,
                                     dropdown=1)
                    if sz: e.component('entry')['width'] = sz
                    fbox.grid(row=row, column=col, columnspan=cspan,
                              sticky=E+W, padx=0, pady=0)
                    e.component('entry')['state'] = state
                    e.pack(expand=1, fill=BOTH)
                    if state == DISABLED:
                        e.component('label')['fg'] = 'red'
                    else:
                        e.component('label')['fg'] = 'black'
                elif validator == TEXT:
                    (w, h) = sz
                    e = Pmw.ScrolledText(self.frame2,
                                         borderframe=1,
                                         text_height=h, text_width=w,
                                         labelpos='w', label_text=fieldname)
                    e.pack(expand=1, fill=BOTH)
                    e.component('text').bind('<Alt-t>', ins_time)
                    if allowattach:
                        e.component('text').bind('<Alt-a>', \
                                                 lambda e, s=self: \
                                                 ins_attachment(e, s))
                    e.component('text').configure(wrap=WORD)
                    if not GuiWindow.showlinks.get():
                        e.component('text').tag_config('experlink', elide=1)
                        e.component('text').tag_config('attachlink', elide=1)
                    else:
                        e.component('text').tag_config('experlink', \
                                                       foreground='red')
                        e.component('text').tag_config('attachlink', \
                                                       foreground='red')
                    e.component('text')['state'] = state
                    if state == DISABLED:
                        e.component('label')['fg'] = 'red'
                    else:
                        e.component('label')['fg'] = 'black'
                elif validator == BOOL:
                    e = Checkbutton2(fbox, text=fieldname, state=state)
                    fbox.grid(row=row, column=col, columnspan=cspan,
                              sticky=W, padx=0, pady=0)
                    e.pack(expand=1, fill=BOTH)
                else:
                    e = Pmw.EntryField(fbox, labelpos='w',
                                       label_text=fieldname, validate=validator)
                    if sz: e.component('entry')['width'] = sz
                    fbox.grid(row=row, column=col, columnspan=cspan,
                              sticky=E+W, padx=0, pady=0)
                    e.component('entry')['state'] = state
                    e.pack(expand=1, fill=BOTH)
                    if state == DISABLED:
                        e.component('label')['fg'] = 'red'
                    else:
                        e.component('label')['fg'] = 'black'

                elist.append(e)
                elist_by_col[col].append(e)

            self._entries[sqlname] = e
            self._validators[sqlname] = validator
            self._converters[sqlname] = converter

        for col in elist_by_col.keys():
            Pmw.alignlabels(elist_by_col[col])

    def keys(self):
        """Get a list of keys (aka fields) for this record.
        """
        return self._entries.keys()

    def setval(self, name, value):
        """Set value of specified field in worksheet.
        """
        if self._converters[name] == sdate:
            self._entries[name].setvalue(sdate(value))
        else:
            self._entries[name].setvalue("%s" % value)
            if self._validators[name] == TEXT:
                txt = self._entries[name].component('text')
                begin = '0.0'
                while 1:
                    # replace EXPER hyperlinks w/ exper widgets
                    begin = txt.search('<elog:exper=.*[0-9]*>',
                                     begin, stopindex=END, regexp=1)
                    if not begin:
                        break
                    end = txt.search('>', begin, stopindex=END)
                    if end:
                        end = end+'+1c'
                        txt.tag_add('experlink', begin, end)

                        (date, exper) = unlink_exper(txt.get(begin, end))
                        if (GuiWindow.showdel.get() or not isdel(date, exper)):
                            ew = ExperWindow(txt, name='%s' % exper,
                                             relief=RIDGE, borderwidth=2)
                            ew.fill(exper=exper, date=date)
                            txt.window_create(end, window=ew, padx=10)
                            self._children.append(ew)
                            self._children_info[ew] = 'exper:%s' % exper
                        begin = end
                begin = '0.0'
                while 1:
                    # replace ATTACHMENT hyperlinks w/ buttons
                    begin = txt.search('<elog:attach=[0-9]*>',
                                     begin, stopindex=END, regexp=1)
                    if not begin:
                        break
                    end = txt.search('>', begin, stopindex=END)
                    if end:
                        end = end+'+1c'
                        txt.tag_add('attachlink', begin, end)
                        id = int(txt.get(begin, end)[1:-1].split('=')[1])
                        im = pil_getattach(id, (128,128))
                        if im is None:
                            # attachement deleted -- go ahead and delete link
                            txt.delete(begin,end)
                        else:
                            b = Button(txt)
                            b.im = im
                            b.config(image=b.im,
                                     command=lambda m=self,id=id: \
                                     AttachmentViewer(m,id))
                            createToolTip(b, 'attachment #%d' % id)
                            txt.window_create(end, window=b, padx=10)
                        begin = end

                txt.see(END)

    def setall(self, dict):
        """Set all values for the worksheet based on values in the dictionary.
        """
        for name in dict.keys():
            if self._entries.has_key(name):
                #self._entries[name].setvalue("%s" % dict[name])
                self.setval(name, dict[name])

    def getval(self, name):
        """Get current on-screen value of indicated field.
        """
        v = self._entries[name].getvalue()
        if self._validators[name] == TEXT:
            v = v[:-1]
        c = self._converters[name]
        if c:
            try:
                return c(v)
            except ValueError:
                return None
        else:
            return v

    def getall(self):
        """Get dictionary of all fields with current on-screen values.
        """
        d = {}
        for k in self.keys():
            d[k] = self.getval(k)
        return d

    def save(self, table, key=(None,None)):
        """Save current on-screen record to specified database table.
        """
        db = getdb()
        
        # for session records only, check to make sure nobody's been
        # messing with the record while you have it open..
        if (table is 'session') and (not key[0] is None):
            rows = db.query("""SELECT lastmod FROM session"""
                            """ WHERE ID=%d""" % key[1])
            last = rows[0]['lastmod']
            if last != self.getval('lastmod'):
                i = warn(self,
                 "\nRecords modified while open. Overwrite changes?\n",
                 ("Overwrite", "Cancel save (discard changes!)"))
                if i > 0:
                    return False
            else:
                # update lastmod with current time in 1/10 secs as the
                # new change time
                self.setval('lastmod', int(10.0*time.time()))

        (keyfield, keyvalue) = key

        names = []
        values = []
        keys = self.keys()
        for k in keys:
            v = self.getval(k)
            if v is not None:
                if type(v) is types.UnicodeType:
                    v = str(v)
                values.append(v)
                names.append(k)
        if keyvalue:
            if not keyfield in keys:
                names.append(keyfield)
                values.append(keyvalue)
            l = ''
            for k in keys:
                if not self.getval(k) is None:
                    v = "'" + str(self.getval(k)).replace("'", "\\'") + "'"
                    if len(l):
                        l = l + ','
                    l = l + "%s=%s" % (k, v)
            db.dquery(READ_ONLY,
                      """UPDATE %s SET %s WHERE %s='%s'""" % \
                        (table, l, keyfield, keyvalue))
        else:
            db.dquery(READ_ONLY,
                      """INSERT INTO %s (%s) VALUES %s""" % \
                        (table, string.join(names, ','), tuple(values)))

        for child in self._children:
            try:
                child.save()
            except:
                # this doesn't seem to matter -- it sometimes happens
                # when trying to save the child exper worksheets, but
                # they seem to get saved anyway -- still can't figure
                # out why..
                Msg('save err: %s' % self._children_info[child])

        Msg("Saved record.")
        
        return True

class DatafileFrame(Frame):
     def __init__(self, master, src, **kwargs):
        Frame.__init__(self, master, **kwargs)

        db = getdb()
        rows = db.query("""SELECT * FROM dfile WHERE src='%s'""" %
                        (src,))

        tag = '%s/%s' % (rows[0]['date'], os.path.basename(src))
        link = "<elog:dfile=%s>" % (tag,)

        f = Frame(self)
        f.pack(expand=1, fill=X)

        self.rv = RecordView(self, layout.DFILE_FIELDS, True)
        self.rv.pack(expand=1, fill=BOTH)
        self.rv.setall(rows[0])
        self.ID = rows[0]['ID']
        
        b = Button(f, text=os.path.basename(src), \
                   command=lambda w=master,l=link: clipcopy(w,l))
        createToolTip(b, 'copy elog link')
        b.pack(side=LEFT)

        b = Button(f, text='fullpath', \
                   command=lambda w=master,l=link: clipcopy(w,"'%s'"%src))
        createToolTip(b, "copy ''%s''" % src)
        b.pack(side=LEFT)

     def save(self):
         self.rv.save(table='dfile',
                      key=('ID', self.ID))

class UnitWindow:
    def __init__(self, exper, unit):
        self.exper = exper
        self.unit = unit

        page = self.exper.getunitbook().add(unit)
        b = Button(page, text='Delete %s' % unit,
                   command=self.delete)
        b.pack(side=TOP, anchor=W)
        createToolTip(b, 'delete unit from database forever!')

        self.rv = RecordView(page, layout.UNIT_FIELDS, True)
        self.rv.pack(side=TOP, expand=1, fill=BOTH)

        d = self.exper.rv.getall()
        db = getdb()
        
        rows = db.query("""SELECT * FROM unit"""
                        """ WHERE animal='%s' AND date='%s' AND"""
                        """ exper='%s' AND unit='%s'""" %
                        (d['animal'], d['date'], d['exper'], unit))
        if len(rows):
            self.rv.setall(rows[0])
        else:
            # new unit, seed the forms

            # Start by inheriting form values from the last day in
            # the database for this animal. However, for some slots
            # this is bad thing (ncorrect etc), so the values are
            # overridden below to resonable starting values

            rows = db.query("""SELECT * FROM unit"""
                            """ WHERE animal='%s'"""
                            """ ORDER BY date DESC LIMIT 1""" %
                            (d['animal'],))
            if len(rows):
                well = rows[0]['well']
            else:
                well = 0

            # override values that shouldn't be inherited from last day:

            self.rv.setall(dict={
                'unit':self.unit,
                'exper':d['exper'],
                'animal':d['animal'],
                'date':d['date'],
                'well':well,
                'crap':0,
                })
        self.rv.pack(side=TOP)

        # this resizes the NoteBook widget to fit the unit view
        self.exper.getunitbook().setnaturalsize()

    def delete(self):
        """Delete this unit from SQL database and delete from GUI.
        """
        i = warn(self.exper,
                 "\nReally delete %s?\n" % self.unit,
                 ("Ok", "Cancel"))
        if i == 0:
            self.save()
            d = self.rv.getall()
            self.exper.unitbook.delete(self.unit)
            self.exper.unitlist.remove(self)
            if len(self.exper.unitlist) == 0:
                self.exper.unitbook.destroy()
                self.exper.unitbook = None

            db = getdb()
            # delete from database -- don't do this the other way around..
            db.dquery(READ_ONLY,
                      """DELETE FROM unit"""
                      """ WHERE animal='%s' AND date='%s' AND"""
                      """ exper='%s' AND unit='%s'""" %
                        (d['animal'], d['date'], d['exper'], self.unit,))

    def save(self):
        """Save unit data to SQL database
        """
        d = self.rv.getall()
        db = getdb()
        rows = db.query("""SELECT * FROM unit"""
                        """ WHERE animal='%s' AND date='%s' AND"""
                        """ exper='%s' AND unit='%s'""" %
                        (d['animal'], d['date'], d['exper'], d['unit'],))
        if len(rows) == 0:
            self.rv.save(table='unit')
        else:
            self.rv.save(table='unit',
                         key=('ID', rows[0]['ID']))

class ExperWindow(Frame):
    def __init__(self, master, name=None, **kwargs):
        Frame.__init__(self, master, **kwargs)

        self.date = None
        self.exper = None

        buttonbar = Frame(self)
        buttonbar.grid(row=0, column=0, sticky=E+W)

        if name:
            Label(buttonbar, text=name).pack(side=LEFT)

        if 0:
            self.tagb = Button(buttonbar, text='+Tag', \
                               command=lambda: self.cloudtag(add=1))
            createToolTip(self.tagb, 'add tag')
            self.tagb.pack(side=LEFT)

            b = Button(buttonbar, text='-Tag', \
                       command=lambda: self.cloudtag(add=0))
            createToolTip(b, 'edit/delete tags')
            b.pack(side=LEFT)
        else:
            self.tagb = None

        b = Button(buttonbar, text='New Unit', \
                   command=self.new_unit)
        createToolTip(b, 'create new unit (TTL etc)')
        b.pack(side=LEFT)

        self.rv = RecordView(self, layout.EXPER_FIELDS, True)
        self.rv.grid(row=1, column=0, sticky=E+W)

        self.unitbook = None
        self.unitlist = []

    def cloudtag(self, add=1):
        print "old tag method", add
        d = self.rv.getall()
        db = getdb()
        if add:
            newtag = cloudtag_select(self)
            if not newtag is None:
                rows = db.query("""SELECT tags,ID FROM exper"""
                                """ WHERE exper='%(exper)s'"""
                                """ AND date='%(date)s'""" % d)
                tags = rows[0]['tags']
                if len(tags) > 0:
                    tags = rows[0]['tags'] + ',' + newtag
                else:
                    tags = newtag
                tags = ",".join(list(set(tags.split(','))))
                db.dquery(READ_ONLY,
                          """UPDATE exper SET tags='%s'"""
                          """ WHERE ID=%d""" % (tags, rows[0]['ID']))
        else:
            rows = db.query("""SELECT tags,ID FROM exper"""
                            """ WHERE exper='%(exper)s'"""
                            """ AND date='%(date)s'""" % d)
            tags = ask(self, 'tags:', rows[0]['tags'])
            if not tags is None:
                tags = ",".join(list(set(tags.split(','))))
                db.dquery(READ_ONLY,
                          """UPDATE exper SET tags='%s'"""
                          """ WHERE ID=%d""" % (tags, rows[0]['ID']))

    def getunitbook(self):
        """Get handle for unit-notebook, or else make one if it doesn't exist.
        """
        if not self.unitbook:
            self.unitbook = Pmw.NoteBook(self)
            self.unitbook.grid(row=2, column=0, sticky=E+W)
            self.unitbook['raisecommand'] = lambda tab,n=self.unitbook: \
                                            raisetab(tab, n)
        return self.unitbook

    def fill(self, dict=None, exper=None, date=None):
        db = getdb()
        if dict:
            self.rv.setall(dict)
            self.date = dict['date']
            self.exper = dict['exper']
        elif exper and date:
            rows = db.query("""SELECT * FROM exper"""
                            """ WHERE exper='%s' AND date='%s'""" %
                            (exper, date,))
            if len(rows) > 0:
                if self.tagb:
                    if len(rows[0]['tags']) > 0:
                        createToolTip(self.tagb, 'tags: ' + rows[0]['tags'])
                    else:
                        createToolTip(self.tagb, 'add tags')
                self.rv.setall(rows[0])
                self.date = date
                self.exper = exper

                rows = db.query("""SELECT * FROM unit"""
                                """ WHERE animal='%s' AND date='%s'"""
                                """ AND exper='%s'""" %
                                (rows[0]['animal'],
                                 rows[0]['date'], rows[0]['exper'],))
                for row in rows:
                    u = UnitWindow(self, row['unit'])
                    self.unitlist.append(u)


        d = self.rv.getall()

        # get list of datafiles
        db = getdb()
        rows = db.query("""SELECT src FROM dfile"""
                        """ WHERE exper='%s' AND date='%s'"""
                        """ ORDER BY ID""" % (exper, date,))
        nr = 3
        self.dfiles = []
        for row in rows:
            w = DatafileFrame(self, row['src'], \
                              borderwidth=2, relief=RIDGE)
            if GuiWindow.showdatafiles.get():
                # only display if the not hidden:
                w.grid(row=nr, column=0, sticky=E+W)
            self.dfiles.append(w)
            nr = nr + 1

    def save(self):
        """
        Save exper to SQL database
        """
        d = self.rv.getall()
        db = getdb()

        # first save all units
        for u in self.unitlist[:]:
            u.save()

        # next save all dfiles
        for df in self.dfiles:
            df.save()

        # then save exper
        rows = db.query("""SELECT ID,exper,date FROM exper"""
                        """ WHERE exper='%s' and date='%s'""" %
                        (d['exper'], d['date'],))
        if len(rows) > 1:
            for n in range(len(rows)):
                print rows[n]
            warn(self, 'database corruption: duplicate exper!')
        else:
            if len(rows) > 0:
                self.rv.save(table='exper',
                             key=('ID', rows[0]['ID']))
            else:
                self.rv.save(table='exper',
                             key=('ID', None))

    def new_unit(self, unit=None):
        d = self.rv.getall()
        db = getdb()
        if unit is None:
            unit = ask(self, 'new unit', 'TTL')
            if unit is None:
                return

        rows = db.query("""SELECT ID FROM unit"""
                        """ WHERE animal='%s' AND date='%s' AND"""
                        """ exper='%s' AND unit='%s'""" %
                        (d['animal'], d['date'], d['exper'], unit,))
        if len(rows) > 0 or unit in self.getunitbook().pagenames():
            warn(self, 'no joy: %s already exists' % unit)
            return 0
        else:
            self.unitlist.append(UnitWindow(self, unit))
            self.getunitbook().selectpage(unit)

class SessionWindow(Frame):
    def __init__(self, master, animal, **kwargs):
        Frame.__init__(self, master, **kwargs)
        
        self.logwin = master
        self.animal = animal
        self.n = 0

        f = Frame(self)

        self.status = Label(f, text="", fg='blue', anchor=W, relief=SUNKEN)
        self.status.pack(side=LEFT, fill=X, expand=1)

        f.pack(side=TOP, fill=X, expand=0, pady=2)

        Msg(window=self.status)

        self.rv = RecordView(self, layout.SESSION_FIELDS, True)
        self.rv.pack(side=BOTTOM, fill=BOTH, expand=1)

    def view(self, date=None):
        db = getdb()
        rows = db.query("""SELECT ID, date FROM session"""
                        """ WHERE animal='%s' ORDER BY date""" %
                        (self.animal,))

        if len(rows) == 0:
            return 0

        if date:
            # iterate through entries to find right date, if it exists..
            n = None
            for i in range(len(rows)):
                if rows[i]['date'] == date or ("%s" % rows[i]['date']) == date:
                    n = i
                    break
            if n is None:
                return 0
            self.n = n

        nmax = len(rows) - 1

        self.n = max(0, min(self.n, nmax))
        rows = db.query("""SELECT * FROM session"""
                        """ WHERE ID=%d ORDER BY date""" %
                        (rows[self.n]['ID'],))
        row = rows[0]
        for k in self.rv.keys():
            self.rv.setval(k, row[k])
        s = '%d/%d recs' % (1+self.n, len(rows),)

        d = self.rv.getall()
        rows = db.query("""SELECT exper FROM exper"""
                        """ WHERE animal='%s' and date='%s'"""
                        """ ORDER BY exper ASC""" %
                        (d['animal'], d['date'],))

        db = getdb()
        shorttitle = "elog:%s" % (d['animal'],)
        GuiWindow.root.winfo_toplevel().title(shorttitle)

        dstr = time.strftime('%a %Y-%m-%d',
                             time.strptime(d['date'], '%Y-%m-%d'))
        Msg(dstr)

        # cache pointer to last record accessed in homedir for next time
        saveConfig(self)

        if self.check() > 0:
            Msg('inserted missing exper; refresh window!')

        return 1

    def save(self):
        d = self.rv.getall()
        db = getdb()
        
        animal = self.rv.getval('animal')
        date = self.rv.getval('date')
        if len(animal) == 0:
            warn(self, "Please specify animal to save.")
            return 0
        if len(date) == 0:
            warn(self, "Please specify date to save.")
            return 0

        rows = db.query("""SELECT ID FROM session"""
                        """ WHERE animal='%s' and date='%s'""" %
                        (d['animal'], d['date'],))
        n = len(rows)

        if n > 1:
            # this is bad, should never happen
            warn(self, 'Duplicated sessionId!')
        elif n == 1:
            # update existing session
            ID = rows[0]['ID']
            e = self.rv.save(table='session',
                             key=('ID', ID))
        else:
            # create entry for a brand new session
            e = self.rv.save(table='session')

        if e:
            Msg("Saved session.")
        return e

    def today(self, date=None):
        """
        Create a new log entry -- default is for TODAY, otherwise for
        the specified date (in the past!)
        """

        animal = self.animal
        if date:
            today = date
        else:
            today = datetime.date(1,1,1).today()

        db = getdb()

        rows = db.query("""SELECT * FROM session"""
                        """ WHERE animal like '%s' and date='%s'""" %
                        (animal, today,))
        if len(rows) > 1:
            warn(self,
                 'Multiple matching records for today.\nTry picking an animal.')
            return
        elif len(rows) == 1:
            # exactly one matching entry, just edit it..
            row = rows[0]
            for k in self.rv.keys():
                self.rv.setval(k, row[k])
        else:
            # this is a new entry...

            #
            # BELOW ARE THE DEFAULT FIELD SETTINGS FOR A NEW ENTRY
            #
            # fill in best guesses and start editing
            if animal == '%':
                # leave animal blank, save will enforce this..
                self.rv.setval("animal", "")
            else:
                self.rv.setval("animal", animal)

            self.rv.setval("user", getuser())
            self.rv.setval("computer", gethost())
            self.rv.setval("date", today)
            self.rv.setval("restricted", "1")
            self.rv.setval("tested", "1")
            self.rv.setval("water_work", "")
            self.rv.setval("water_sup", "")
            self.rv.setval("fruit", "")
            self.rv.setval("fruit_ml", "")
            self.rv.setval("weight", "")
            self.rv.setval("note", "")
            self.rv.setval("ncorrect", "0")
            self.rv.setval("ntrials", "0")

        self.n = 1e6

    def find_bydate(self):
        s = ask(self, 'find date (YYYY-MM-DD)', '')
        if s:
            ss = string.split(s, '-')
            if len(ss) != 3:
                warn(self, "Invalid date: '%s'" % s)
            elif not self.view(date=s):
                warn(self, "Can\'t find date: '%s'" % s)

    def find_byexper(self):
        d = self.rv.getall()
        db = getdb()
        s = ask(self, 'find exper/cell id (%s only)' % d['animal'], '')
        if s:
            # only look in current animal..
            rows = db.query("""SELECT date FROM dfile """
                            """ WHERE exper='%s' and animal='%s'""" %
                            (s, d['animal']))
            if len(rows) == 0:
                warn(self, "Can\'t find exper: %s" % s)
            else:
                d = rows[0]['date']
                if not self.view(date=d):
                    warn(self, "Can\'t find date: '%s'" % d)

    def check(self):
        """Check database to see if entry for specified date is
        missing exper-hyperlinks (inaccessible expers..)
        """
        d = self.rv.getall()
        db = getdb()
        animal = d['animal']
        date = d['date']

        missing = 0
        # find all exper's that don't have a hyperlink in a note field
        rows = db.query("""SELECT exper,date FROM exper"""
                        """ WHERE animal='%s' and date='%s'""" %
                        (animal, date,))
        for row in rows:
            if int(row['exper'][-4:]) > 0:
                link = "<elog:exper=%s/%s>" % (row['date'], row['exper'])
                if string.find(d['note'], link) < 0:
                    sys.stderr.write('elog: %s in database, but not linked\n' % link)
                    missing = missing + 1
                    d['note'] = d['note'] + '\n' + link + '\n'

        if missing > 0:
            self.rv.setall(d)

        return missing

class GuiWindow(Frame):
    root = None
    def __init__(self, master, animal='%', ro=False, **kwargs):

        self.animal = animal

        GuiWindow.root = master

        Frame.__init__(self, master, **kwargs)

        menu = Pmw.MenuBar(self, hull_relief=RAISED, hull_borderwidth=1,
                           hotkeys=False)

        menu.addmenu('File', '', '')
        menu.addmenuitem('File', 'command', label='Save (Ctrl-S)',
                         command=self.save)
        menu.addmenuitem('File', 'command', label='Exit w/out save',
                         command=lambda tk=master: die(tk))
        menu.addmenuitem('File', 'command', label='Save & Quit (Ctrl-Q)',
                         command=self.quit)

        menu.addmenu('Edit', '', '')
        menu.addmenuitem('Edit', 'command', label='Find session by date',
                         command=lambda s=self: s.session.find_bydate())
        menu.addmenuitem('Edit', 'command', label='Find session by exper/cell',
                         command=lambda s=self: s.session.find_byexper())

        GuiWindow.showlinks = IntVar()
        GuiWindow.showlinks.set(0)

        GuiWindow.showdel = IntVar()
        GuiWindow.showdel.set(0)

        GuiWindow.showdatafiles = IntVar()
        GuiWindow.showdatafiles.set(0)

        menu.addmenuitem('Edit', 'checkbutton', label='show data files',
                         variable=GuiWindow.showdatafiles,
                         command=lambda s=self:s.refresh())

        menu.addmenuitem('Edit', 'checkbutton', label='show links',
                         variable=GuiWindow.showlinks,
                         command=lambda s=self:s.refresh())

        menu.addmenuitem('Edit', 'checkbutton', label='show deleted',
                         variable=GuiWindow.showdel,
                         command=lambda s=self:s.refresh())

        menu.addmenuitem('Edit', 'separator')
        menu.addmenuitem('Edit', 'command', label='Attach window (Alt-A)',
                         command=lambda s=self: info(s,
                         """Type Alt-A in text window, then """
                         """click in window to attach."""))

        menu.addmenu('Animals', '', '')
        for a in find_animals(getdb()):
            menu.addmenuitem('Animals', 'command', label=a,
                             command=lambda s=self,a=a,tk=master: \
                             s.selanimal(tk,a))

        menu.pack(side=TOP, expand=0, fill=X)

        menuhull = Frame(menu.component('hull'))
        menuhull.pack(side=LEFT)

        if ro:
            Label(menuhull, text='READ-ONLY',
                  fg='red', padx=10).pack(side=LEFT, expand=0)

        b = Button(menuhull, text='Refresh',
                   command=lambda s=self: s.refresh())
        createToolTip(b, 'refresh gui window (Alt-R)')
        b.pack(side=LEFT)

        b = Button(menuhull, text='New Exper',
                   command=lambda s=self: s.new_exper())
        createToolTip(b, 'create new numbered exper/rec-site in database (Alt-N)')
        b.pack(side=LEFT)

        createToolTip(b, 'go to today')
        b.pack(side=LEFT, expand=0)
        b = Button(menuhull, text='Today',
                   command=lambda s=self: s.session.today())
        createToolTip(b, 'go to today')
        b.pack(side=LEFT, expand=0)

        b = Button(menuhull, text='|<',
                   command=lambda s=self: s.jump(-1e6))
        createToolTip(b, 'first record (Alt-Ctl-Home)')
        b.pack(side=LEFT, expand=0)
        b = Button(menuhull, text='<<',
                   command=lambda s=self: s.jump(-10))
        createToolTip(b, 'go back 10 (Alt-Ctl-PageUp)')
        b.pack(side=LEFT, expand=0)
        b = Button(menuhull, text='<',
                   command=lambda s=self: s.jump(-1))
        createToolTip(b, 'go back 1 (Alt-PageUp)')
        b.pack(side=LEFT, expand=0)
        b = Button(menuhull, text='>',
                   command=lambda s=self: s.jump(1))
        createToolTip(b, 'go forward 1 (Alt-PageDown)')
        b.pack(side=LEFT, expand=0)
        b = Button(menuhull, text='>>',
                   command=lambda s=self: s.jump(10))
        createToolTip(b, 'go forward 10 (Alt-Ctl-PageDown)')
        b.pack(side=LEFT, expand=0)
        b = Button(menuhull, text='>|',
                   command=lambda s=self: s.jump(1e6))
        createToolTip(b, 'go to end (Alt-Ctl-End)')
        b.pack(side=LEFT, expand=0)

        self.session = None
        self.jump(1e6)

    def selanimal(self, tk, animal):
        if self.session:
            self.session.save()
            self.session.destroy()
            self.session = None
        self.animal = animal
        self.jump(1e6)

    def refresh(self):
        self.jump(0)

    def jump(self, n, save=1):
        db = getdb()
        if self.session:
            n = self.session.n + n
            # update dtb.. get last 7 testing dayes
            animal = self.session.rv.getval('animal')
            date = self.session.rv.getval('date')
            kg = self.session.rv.getval('weight')
            rows = db.query("""SELECT date,water_work,weight FROM """\
                            """ session WHERE""" \
                            """ animal='%s' and date<'%s' and""" \
                            """ water_work > 0 and"""\
                            """ restricted=1 and tested=1 ORDER""" \
                            """ BY date DESC LIMIT 7""" % \
                            (self.animal, date,))
            wt = np.array([r['weight'] for r in rows])
            try:
                # dtb is (mean-2sigma) working intake ml/kg for last 7 days
                # note: this value can drop below zero, so it's forced >=0
                #
                # dtb is water dose is ml/kg
                # dtb_ml is volume (based on dtb and animal weight)
                # dtb/dtb_ml are clip to a minimum of 10 ml/kg
                # xdtb/xdtb_ml are clipped to a 0 ml/kg
                dt = np.array([r['water_work'] for r in rows]) / wt
                if len(dt):
                    xdtb = max(0, np.mean(dt) - 2.0 * np.std(dt))
                else:
                    xdtb = 0.0
                dtb = max(MINDTB, xdtb)
                self.session.rv.setval('xdtb', round(xdtb,1))
                self.session.rv.setval('dtb', round(dtb,1))
            except:
                #warn(self, 'DTB Calc: error occurred, check', timeout=1000)
                dtb = -1.0
                xdtb = -1.0

            if kg is None:
                self.session.rv.setval('dtb_ml', 0.0)
                self.session.rv.setval('xdtb_ml', 0.0)
            else:
                self.session.rv.setval('dtb_ml', round(dtb*kg,1))
                self.session.rv.setval('xdtb_ml', round(xdtb*kg,1))

            tf = 0.0
            for x in ['water_work', 'water_sup', 'fruit_ml']:
                f = self.session.rv.getval(x)
                if f is not None: tf += f
            self.session.rv.setval('totalfluid', tf)

            if save:
                self.session.save()
            self.session.destroy()

        self.session = SessionWindow(self, self.animal)
        self.session.pack(expand=1, fill=BOTH, anchor=N)
        self.session.n = n
        self.session.view()

    def exists(self, animal, date):
        db = getdb()
        rows = db.query("""SELECT ID, date FROM session"""
                        """ WHERE animal='%s' AND date='%s'"""
                        """ ORDER BY date""" %
                        (animal, date,))
        return len(rows) > 0

    def quit(self):
        saveConfig(self.session)
        self.save()
        self.destroy()

    def save(self):
        if self.session.save():
            Msg("Saved.")
        else:
            Msg("Saved canceled.")
        return 1

    def view(self, date=None, exper=None):
        self.session.view(date=date)

    def next_exper(self):
        db = getdb()
        rows = db.query("""SELECT exper FROM exper"""
                        """ WHERE animal like '%s'"""
                        """ ORDER BY exper DESC LIMIT 1""" %
                        (self.animal,))
        pre = self.animal
        num = 0
        if len(rows) > 0:
            try:
                exper = rows[0]['exper']
                pre = exper[:-4]
                num = int(exper[-4:]) + 1
            except ValueError:
                pass
        guess = "%s%04d" % (pre, num)
        return ask(self, 'new exper', guess)

    def new_exper(self):
        exper = self.next_exper()
        if exper is None or len(exper) <= 0:
            return

        self.session.save()
        d = self.session.rv.getall()
        date = self.session.rv.getval('date')
        db = getdb()
        
        # insert empty new exper in the database
        db.dquery(READ_ONLY,
                  """INSERT INTO exper (exper, animal, date, time)"""
                  """ VALUES %s""" %
                      ((exper, self.animal, date, time.strftime('%H%M-')),))

        link = "\n<elog:exper=%s/%s>\n" % (d['date'], exper)
        note = d['note'] + link

        rows = db.query("""SELECT ID FROM session"""
                        """ WHERE animal='%s' and date='%s'""" %
                        (d['animal'], d['date'],))
        ID = rows[0]['ID']

        # following command is the problem!! REPLACE deletes row
        # first.. should be UPDATE instead.. record already should
        # exist!
        db.dquery(READ_ONLY,
                  """UPDATE session SET animal='%s', date='%s', note='%s'"""
                  """ WHERE ID=%d""" %
                    (d['animal'], d['date'],
                    str(note).replace("'", "\\'"), ID),)

        self.jump(0, save=0)

def _configFile():
    import os
    return os.path.expanduser('~/.elogrc')

def saveConfig(session):
    import ConfigParser

    c = ConfigParser.ConfigParser()
    c.add_section('elog')
    c.set('elog', 'animal', session.rv.getval('animal'))
    c.set('elog', 'date', session.rv.getval('date'))
    c.set('elog', 'show_data', session.logwin.showdatafiles.get())
    c.set('elog', 'show_links', session.logwin.showlinks.get())
    c.set('elog', 'show_deleted', session.logwin.showdel.get())

    with open(_configFile(), 'w') as f:
        c.write(f)

def readConfig(session):
    import ConfigParser

    c = ConfigParser.ConfigParser()
    try:
        with open(_configFile(), 'r') as f:
            c.readfp(f)
    except IOError:
        c.add_section('elog')
        c.set('elog', 'animal', '')
        c.set('elog', 'date', '')
    return c
            
#############################################################3

def usage(badarg=None, exit=1):
    sys.stderr.write("""\
mlab database-backed electronic log notebook tool
usage: %s [options] [date] [exper]

General options:
  -r/-ro                   read only mode!
  -info                    list animals in database to stdout (and exit)
  -q                       query animal and date info from user
  -animal=<animal name>    select animal *FULL NAME, NOT ABBREV*
  -new                     flag to allow creation of new animal
  -date                    query for date from user
  -date=YYYY-MM-DD         jump to specified date (-1 for yesterday etc)
  -exper=PREFIXnnnnn       jump to date of 'exper'
  -today                   requires -animal as well!
  -last                    open at last entry

Dump options:
  -dump[=N]                dump html to console; N<0 work backwards from now.
  -out=dir                 name of dump directory
  -rev                     reverse order of dump (ie, most recent first)
  -y                       force yes answer to create-new-entry questions
Datafile options:
  -data file1..fileN       add new datafiles to sql db (won't overwrite)
  -forcedata file1..fileN  add new datafiles, but overwrites existing records
""" % os.path.basename(sys.argv[0]))
    if badarg:
        sys.stderr.write(' Unknown option: "%s"\n' % badarg)
        sys.exit(1)
    if exit:
        sys.exit(1)

def animallist():
    s = string.join(find_animals(getdb()), ' ')
    if len(s) > 0:
        return s
    else:
        return 'None'

def require_tk(tk):
    if tk is None:
        sys.stderr.write('elog: Can\'t initialize GUI\n')
        sys.exit(0)

def start():
    import datetime
    import calendar

    global READ_ONLY

    if len(getuser()) == 0:
        sys.stderr.write('elog: no user information available!\n')
        sys.exit(1)

    if len(gethost()) == 0:
        sys.stderr.write('elog: no host/computer name available!\n')
        sys.exit(1)

    tk = None

    animal = None
    dump = None
    outdir = None
    rev = None
    date = None
    exper = None
    dfile = None
    files = []
    init = None                         # initialize fresh database
    info = None
    new = 0
    force_yes = 0
    last = 0
    READ_ONLY = False

    try:
        tk = Tk()
        #tk.tk_setPalette(background='yellow', foreground='black')
        tk.withdraw()
        Pmw.initialise(tk, size=8)
        #tk.option_add("*DisabledForeground", 'black')
        #tk.option_add("*Background", 'white')
        #tk.option_add("*selectBackground", 'blue')
        
        tk.option_add("*Entry.Font", 'TkFixedFont')
        tk.option_add("*Text.Font", 'TkFixedFont')
        
        #tk.option_add("*Scrollbar.background", 'black')
        #tk.option_add("*Scrollbar.troughColor", 'gray50')
        #tk.option_add("*Scrollbar.activeBackground", 'blue')
        

    except:
        tk = None

    for arg in sys.argv[1:]:
        if arg[0:2] == '--':
            arg = arg[1:]
            
        if isarg(arg, '-dir'):
            import dbsettings
            sys.stdout.write('%s\n' % dbsettings.DIR)
            sys.exit(0)
        elif isarg(arg, '-db'):
            import dbsettings
            # print `env` suitable string to stdout with DB info
            sys.stdout.write('HOST=%s ' % dbsettings.HOST)
            sys.stdout.write('USER=%s ' % dbsettings.USER)
            sys.stdout.write('PASS=%s ' % dbsettings.PASS)
            sys.stdout.write('DB=%s ' % dbsettings.DB)
            sys.stdout.write('PORT=%s\n' % dbsettings.PORT)
            sys.exit(0)
        elif isarg(arg, '-y'):
            force_yes = 1
        elif isarg(arg, '-rev'):
            rev = 1
        elif isarg(arg, '-r') or isarg(arg, '-ro'):
            READ_ONLY = True
        elif isarg(arg, '-info'):
            info = 1
        elif isarg(arg, '-q'):
            require_tk(tk)
            animal = tkdialogs.select(find_animals(getdb()))
            if animal is None:
                sys.exit(0)
            require_tk(tk)
            date = tkdialogs.getdate(tk)
            if date is None:
                sys.exit(0)
        elif isarg(arg, '-animal='):
            animal = string.split(arg, '=')[1]
        elif isarg(arg, '-animal'):
            require_tk(tk)
            animal = tkdialogs.select(find_animals(getdb()))
            if animal is None:
                sys.exit(0)
        elif isarg(arg, '-a'):
            animal = arg[2:]
        elif isarg(arg, '-new'):
            new = 1
        elif isarg(arg, '-date='):
            date = string.split(arg, '=')[1]
            try:
                # -1 for yesterday, etc..
                date = datetime.datetime.now() + \
                  datetime.timedelta(days=int(date))
                date = date.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    # try to use the clever parsedatetime module to handle
                    # stuff like 'yesterday' etc..
                    import parsedatetime as pdt
                    p = pdt.Calendar(pdt.Constants()).parse(date)
                    if p[1] != 1:
                        # assume it's a YYYY-MM-DD string..
                        date = date
                    else:
                        date = '%04d-%02d-%02d' % \
                          (p[0].tm_year,p[0].tm_mon,p[0].tm_mday,)
                except ImportError:
                    pass
        elif isarg(arg, '-date'):
            require_tk(tk)
            date = tkdialogs.getdate(tk)
            if date is None:
                sys.exit(0)
        elif isarg(arg, '-exper='):
            exper = string.split(arg, '=')[1]
        elif isarg(arg, '-today'):
            date = '%s' % datetime.date(1,1,1).today()
        elif isarg(arg, '-last'):
            last = 1
        elif isarg(arg, '-dump='):
            dump = 1
            count = int(string.split(arg, '=')[1])
        elif isarg(arg, '-dump'):
            dump = 1
            count = 0
        elif isarg(arg, '-out='):
            outdir = string.split(arg, '=')[1]
        elif isarg(arg, '-data'):
            dfile = 1
            force = None
        elif isarg(arg, '-forcedata'):
            dfile = 1
            force = 1
        elif isarg(arg, '-help'):
            usage()
        elif os.path.exists(arg):
            # datafile to add
            files.append(arg)
        elif re.match('^[0-9]...-[0-9].-[0-9].*/[a-z]*[0-9]...$', arg):
            date = arg[0:10]
            exper = arg[11:]
        elif re.match('^[a-z]*[0-9]...$', arg):
            exper = arg
        elif re.match('^[0-9]...-[0-9].-[0-9].*$', arg):
            date = arg
        elif arg in find_animals(getdb()):
            animal = arg
        else:
            sys.stderr.write('elog: unknown arg -- %s\n' % arg)
            sys.exit(1)

    cfg = readConfig(None)
    _animal = cfg.get('elog', 'animal')
    _date = cfg.get('elog', 'date')

    if not dump and animal is None:
        animal = _animal
    if not dump and date is None:
        date = _date

    if info:
        sys.stdout.write(animallist())
        sys.stdout.write('\n')
        sys.exit(0)

    if dump and animal is None:
        sys.stderr.write("elog: -dump requires -animal\n")
        sys.exit(0)

    if exper:
        (animal, date) = find_expers(Database(), exper)
        if animal is None:
            sys.exit(0)

    alist = find_animals(getdb())

    if (animal not in alist):
        if animal == '':
            sys.stderr.write("elog: specify animal or use -new\n")
            sys.exit(0)
        elif (not new):
            sys.stderr.write("elog: '%s' doesn't exist, use -new\n" % animal)
            sys.exit(0)
        else:
            if date is None:
                date = datetime.date(1,1,1).today()

    if dfile:
        find_pype()
        try:
            for f in files:
                if not insert_dfile(Database(), f, force=force):
                    sys.exit(1)
        finally:
            Database().close()
        sys.exit(0)

    if dump:
        if outdir is None:
            sys.stderr.write('elog: dump requires output directory\n')
            sys.exit(1)
        dumphtml.dump(outdir, Database(),
                      animal, count, rev=rev, date=date)
        Database().close()
        sys.exit(0)

    require_tk(tk)
    
    logwin = GuiWindow(tk, animal=animal, ro=READ_ONLY)

    if date:
        dow = ''
        try:
            # allow for date=-1 for yesterday, etc..
            x = int(date)
            d_ = (datetime.date.today() + datetime.timedelta(int(x)))
            realdate = '%s' % d_
            date = realdate
            dow = ' (%s)' % calendar.day_name[d_.weekday()]
        except ValueError:
            pass
        except TypeError:
            pass

        if not logwin.exists(animal=animal, date=date):
            if not force_yes:
                sys.stderr.write("""elog: animal=\'%s\' """
                                 """date=%s%s not in database.\n""" % \
                                 (animal, date, dow))
            if animal is None:
                sys.stderr.write('elog: -animal required with -new\n')
                sys.exit(1)
            else:
                if not force_yes and \
                       not askyesno(tk, 'elog',
                                    "Create new entry: '%s' on %s%s?" % \
                                    (animal, date, dow)):
                    sys.exit(0)
                logwin.session.today(date=date)
                logwin.save()

    logwin.pack(fill=BOTH, expand=1, anchor=NW)

    logwin.view(date=date)
    if last:
        logwin.jump(1e6)

    if 0:
        logwin.bind_all('<Control-KeyPress-x>',
                        lambda e, tk=tk: die(tk))
    logwin.bind_all('<Control-KeyPress-q>',
                    lambda e, w=logwin: w.quit())
    logwin.bind_all('<Control-KeyPress-s>',
                    lambda e, w=logwin: w.save())
    logwin.bind_all('<Alt-KeyPress-n>',
                    lambda e, w=logwin: w.new_exper())
    logwin.bind_all('<Alt-KeyPress-r>',
                    lambda e, w=logwin: w.refresh())
    logwin.bind_all('<Alt-KeyPress-Next>',
                    lambda e, w=logwin: w.jump(1))
    logwin.bind_all('<Alt-KeyPress-Prior>',
                    lambda e, w=logwin: w.jump(-1))
    logwin.bind_all('<Alt-Control-KeyPress-Next>',
                    lambda e, w=logwin: w.jump(10))
    logwin.bind_all('<Alt-Control-KeyPress-Prior>',
                    lambda e, w=logwin: w.jump(-10))
    logwin.bind_all('<Alt-Control-Home>',
                    lambda e, w=logwin: w.jump(-1e6))
    logwin.bind_all('<Alt-Control-End>',
                    lambda e, w=logwin: w.jump(1e6))

    tk.protocol("WM_DELETE_WINDOW", logwin.quit)
    tk.deiconify()
    if cfg is not None:
        logwin.showdatafiles.set(cfg.get('elog', 'show_data'))
        logwin.showlinks.set(cfg.get('elog', 'show_links'))
        logwin.showdel.set(cfg.get('elog', 'show_deleted'))
    
    logwin.jump(0)
    tk.wait_window(logwin)

