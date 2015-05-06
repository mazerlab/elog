#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
import os
import string
import types
import datetime, time

################################################################

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
    
################################################################

def dtbhist(animal, INTERVAL=7):
    import numpy as np
	import matplotlib.dates as mdates
    
    
    db = getdb()
    
    rs = db.query("""SELECT * FROM session WHERE """
                  """  animal='%s' """
                  """  ORDER BY date """ % (animal,))

    dates = np.array([mdates.strpdate2num('%Y-%m-%d')('%s'%r['date']) for r in rs])

    m = np.zeros((len(rs), 5))
                 
    for n in range(0, len(rs)):
        v = []
        for k in range(n-1, 0, -1):
            r = rs[k]
            if r['water_work'] and r['weight'] and \
              r['tested'] and r['restricted']:
                v.append(r['water_work']/r['weight'])
            if len(v) >= INTERVAL:
                break
        v = np.array(v)
        dtb = round(max(10.0, np.mean(v) - (2 * np.std(v))))
        dtb_ml = -1
        if rs[n]['weight']:
            dtb_ml = round(dtb * rs[n]['weight'])
        else:
            dtb_ml = np.nan
        xdtb = round(max(0.0, np.mean(v) - (2 * np.std(v))))

        if rs[n]['weight']:
            xdtb_ml = round(xdtb * rs[n]['weight'])
        else:
            xdtb_ml = np.nan

        m[n, 0] = dates[n]
        m[n, 1] = dtb
        m[n, 2] = dtb_ml
        m[n, 3] = xdtb
        m[n, 4] = xdtb_ml
    return m


if __name__ == '__main__':
    db = getdb()
    animals = [r['animal'] for r in
               db.query("""SELECT animal FROM animal """
                        """ WHERE animal NOT LIKE '%test%' """)]
    
    for a in animals:
        print dtbhist(a)

"""
Failure modes:

- water_work == 0 -- this is usually because tested should be unchecked!
     ... water_work > 0 AND water_work IS NOT NULL ...
- no weight entered on a work day..     

"""            
