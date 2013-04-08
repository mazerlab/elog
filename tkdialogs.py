#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

# calendar code from:
# Source: http://pythonical.sourceforge.net/dlgCalendar.py
# Original Author: Camilo Olarte|colarte@telesat.com.co|Sept.2003

import Tkinter
Tk = Tkinter

import Pmw_1_3_2 as Pmw

def today():
    import time
    return (time.localtime()[0], time.localtime()[1], time.localtime()[2], )

class tkCalendar:
    strdays = "Su  Mo  Tu  We  Th  Fr  Sa"
    dictmonths = {'1':'Jan','2':'Feb','3':'Mar','4':'Apr',
                  '5':'May','6':'Jun','7':'Jul','8':'Aug',
                  '9':'Sep','10':'Oct','11':'Nov', '12':'Dec'}
    
    def __init__ (self, master, year=None, month=None, var=None):
        if year is None:
            year, x, x = today()
        if month is None:
            x, month, x = today()

        self.update_var = var
        self.top = Tk.Toplevel(master)
        
        self.intmonth = month

        self.canvas =Tk.Canvas(self.top, width=200, height=220, relief=Tk.RIDGE,
                               background ="white", borderwidth =1)
        self.canvas.create_rectangle(0,0,303,30, fill="#a4cae8",width=0 )
        self.canvas.create_text(100,17, text='Select Date', fill="#2024d6")
        stryear = str(year)

        self.year_var=Tk.StringVar()
        self.year_var.set(stryear)
        self.lblYear = Tk.Label(self.top, textvariable=self.year_var, 
                                background="white")
        self.lblYear.place(x=85, y=30)

        self.month_var = Tk.StringVar()
        strnummonth = str(self.intmonth)
        strmonth = tkCalendar.dictmonths[strnummonth]
        self.month_var.set(strmonth)

        self.lblYear = Tk.Label(self.top, textvariable=self.month_var, 
                                background="white")
        self.lblYear.place(x=85, y=50)
        
        tagBaseButton = "Arrow"
        self.tagBaseNumber = "DayButton"
        
        #draw year arrows
        x,y = 40, 43
        tagThisButton = "leftyear"  
        tagFinalThisButton = tuple((tagBaseButton,tagThisButton))
        self.CreateLeftArrow(self.canvas, x,y, tagFinalThisButton)
        x,y = 150, 43
        tagThisButton = "rightyear"  
        tagFinalThisButton = tuple((tagBaseButton,tagThisButton))
        self.CreateRightArrow(self.canvas, x,y, tagFinalThisButton)
        
        #draw month arrows
        x,y = 40, 63
        tagThisButton = "leftmonth"  
        tagFinalThisButton = tuple((tagBaseButton,tagThisButton))
        self.CreateLeftArrow(self.canvas, x,y, tagFinalThisButton)
        x,y = 150, 63
        tagThisButton = "rightmonth"  
        tagFinalThisButton = tuple((tagBaseButton,tagThisButton))
        self.CreateRightArrow(self.canvas, x,y, tagFinalThisButton)
        
        #Print days 
        self.canvas.create_text(100,90, text=tkCalendar.strdays)
        self.canvas.pack (expand=1, fill=Tk.BOTH)
        self.canvas.tag_bind ("Arrow", "<ButtonRelease-1>", self.Click)
        self.canvas.tag_bind ("Arrow", "<Enter>", self.OnMouseOver)
        self.canvas.tag_bind ("Arrow", "<Leave>", self.OnMouseOut)
        
        self.FillCalendar()
        
        f = Tk.Frame(self.top)
        f.pack(expand=1, fill=Tk.X)

        todayb = Tk.Button(f, text='Today (Ret)', command=self.TodayCB)
        todayb.pack(side=Tk.LEFT, fill=Tk.X, expand=1)
        
        cancelb = Tk.Button(f, text='Cancel (Esc)', command=self.CancelCB)
        cancelb.pack(side=Tk.LEFT, fill=Tk.X, expand=1)

        self.top.protocol('WM_DELETE_WINDOW', self.CancelCB)

        self.top.bind ("<Return>", lambda ev,s=self: s.TodayCB())
        self.top.bind ("<Escape>", lambda ev,s=self: s.CancelCB())
        

    def CreateRightArrow(self, canv, x, y, strtagname):
        canv.create_polygon(x,y, [[x+0,y-5], [x+10, y-5], [x+10,y-10] , 
                    [x+20,y+0], [x+10,y+10], [x+10,y+5], [x+0,y+5]],
                    tags=strtagname, fill="blue", width=0)

    def CreateLeftArrow(self, canv, x, y, strtagname):
        canv.create_polygon(x,y, [[x+10,y-10], [x+10, y-5], [x+20,y-5], 
                    [x+20,y+5], [x+10,y+5], [x+10,y+10] ],
                    tags=strtagname, fill="blue", width=0)

    def Click(self,event):
        owntags = self.canvas.gettags(Tk.CURRENT)
        if "rightyear" in owntags:
            intyear = int(self.year_var.get())
            intyear +=1
            stryear = str(intyear)
            self.year_var.set(stryear)
        if "leftyear" in owntags:
            intyear = int(self.year_var.get())
            intyear -=1
            stryear = str(intyear)
            self.year_var.set(stryear)
        if "rightmonth" in owntags:
            if self.intmonth < 12 :
                self.intmonth += 1 
                strnummonth = str(self.intmonth)
                strmonth = tkCalendar.dictmonths[strnummonth]
                self.month_var.set(strmonth)
            else :
                self.intmonth = 1 
                strnummonth = str(self.intmonth)
                strmonth = tkCalendar.dictmonths[strnummonth]
                self.month_var.set(strmonth)
                intyear = int(self.year_var.get())
                intyear +=1
                stryear = str(intyear)
                self.year_var.set(stryear)
        if "leftmonth" in owntags:
            if self.intmonth > 1 :
                self.intmonth -= 1 
                strnummonth = str(self.intmonth)
                strmonth = tkCalendar.dictmonths[strnummonth]
                self.month_var.set(strmonth)
            else :
                self.intmonth = 12
                strnummonth = str(self.intmonth)
                strmonth = tkCalendar.dictmonths[strnummonth]
                self.month_var.set(strmonth)
                intyear = int(self.year_var.get())
                intyear -=1
                stryear = str(intyear)
                self.year_var.set(stryear)
                
        self.FillCalendar()	    

    def FillCalendar(self):
        import calendar
        
        init_x_pos = 20
        arr_y_pos = [110,130,150,170,190,210]
        intposarr = 0
        self.canvas.delete("DayButton")
        self.canvas.update()
        intyear = int(self.year_var.get())
        calendar.setfirstweekday(6)
        monthcal = calendar.monthcalendar(intyear, self.intmonth)
        for row in monthcal:
            xpos = init_x_pos 
            ypos = arr_y_pos[intposarr]
            for item in row:	
                stritem = str(item)
                if stritem == "0":
                    xpos += 27
                else :
                    tagNumber = tuple((self.tagBaseNumber,stritem))
                    self.canvas.create_text(xpos, ypos, text=stritem, 
                                            tags=tagNumber)
                    xpos += 27
            intposarr += 1
        self.canvas.tag_bind ("DayButton", "<ButtonRelease-1>", self.SelectDate)
        self.canvas.tag_bind ("DayButton", "<Enter>", self.OnMouseOver)
        self.canvas.tag_bind ("DayButton", "<Leave>", self.OnMouseOut)   

    def OnMouseOver(self,event):
        self.canvas.move(Tk.CURRENT, -2, -2)
        self.canvas.update()

    def OnMouseOut(self,event):
        self.canvas.move(Tk.CURRENT, 2, 2)
        self.canvas.update()

    def SelectDate(self,event):
        owntags = self.canvas.gettags(Tk.CURRENT)
        for x in owntags:
            if not ((x == "current") or (x == "DayButton")):
                self.strdate = '%s-%02d-%02d' % \
                               (self.year_var.get(), self.intmonth, int(x))
                if self.update_var:
                    self.update_var.set(self.strdate)
                    self.top.destroy()
                    
    def CancelCB(self):
        if self.update_var:
            self.update_var.set('')
            self.top.destroy()

    def TodayCB(self):
        if self.update_var:
            self.update_var.set('%4d-%02d-%02d' % today())
            self.top.destroy()
            

def getdate(master):
    v = Tk.StringVar()
    w = tkCalendar(master, None, None, v)
    master.wait_window(w.top)
    d = v.get()
    if len(d):
        return d
    else:
        return None

class tkSelector:
	def __init__(self, items, title=None):
        self.dialog = Pmw.SelectionDialog(master = None,
                                          title = 'Select one...',
                                          label_text = title,
                                          buttons=('OK', 'Cancel'),
                                          defaultbutton='OK',
                                          scrolledlist_labelpos='n',
                                          scrolledlist_items=items,
                                          command=self.execute)
        self.dialog.pack(fill='both', expand=1, padx=5, pady=5)

	def go(self):
        self.dialog.activate()
		self.dialog.destroy()
		return self.result

	def execute(self, buttonname):
        sels = self.dialog.getcurselection()
		if buttonname is None or buttonname is 'Cancel' or len(sels) == 0:
			self.result = None
		else:
			self.result = sels[0]
		self.dialog.deactivate()

def select(items):
	return tkSelector(items).go()
    

if __name__ == '__main__':
    root = Tk.Tk()
    root.withdraw()
    print getdate(root)
	#print select(root, ('foo', 'bar', 'baz', ))
