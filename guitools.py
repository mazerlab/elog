#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
import time

from Tkinter import *
import tkFont
import tkMessageBox
import PmwBundle as Pmw

def ins_time(event):
    """Insert current timestamp into text widget.
    """
    event.widget.insert(INSERT, time.strftime('%H%Mh: '))

def die(tk):
    """Immediate quit w/o save!
    """
    tk.destroy()
    sys.exit(0)

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

def popup(w):
    w.winfo_toplevel().deiconify()
    w.winfo_toplevel().lift()

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

def info(master, mesg, **kwargs):
    warn(master, mesg, title='Info', icon_bitmap=None, **kwargs)

def warn(master, mesg, buttons=("Dismiss",), timeout=None,
         title='Warning', icon_bitmap='warning'):
    """
    Simple warning message dialog box
    """
    x, y = master.winfo_pointerxy()   # -1 if off screen
    w = Pmw.MessageDialog(master,
                          iconpos='w',
                          icon_bitmap=icon_bitmap,
                          title=title,
                          buttons=buttons,
                          defaultbutton=0,
                          message_text=mesg)
    x = max(1, x - (w.winfo_width() / 2) - 10)
    y = max(1, y - (w.winfo_height() / 2) - 10)
    if timeout:
        w.after(timeout, lambda w=w: w.destroy())
        w.activate(geometry='+%d+%d' % (x,y))
    else:
        return w.activate(geometry='+%d+%d' % (x,y))

def askyesno(master, title, msg, icon_bitmap='warning'):
    """
    Simple yes/no dialog box under mouse
    """
    x, y = master.winfo_pointerxy()   # -1 if off screen
    vis = master.winfo_viewable()
    if not vis:
        master.deiconify()
    
    w = Pmw.MessageDialog(master,
                          iconpos='w',
                          icon_bitmap=icon_bitmap,
                          title=title,
                          buttons=("Yes", "No"),
                          defaultbutton=0,
                          message_text=msg)
    x = max(1, x - (w.winfo_width() / 2) - 10)
    y = max(1, y - (w.winfo_height() / 2) - 10)
    choice = w.activate(geometry='+%d+%d' % (x,y)) == "Yes"
    if not vis:
        master.withdraw()
    
    return choice
    
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
