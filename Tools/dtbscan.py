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

if __name__ == '__main__':
    import numpy as np
    
    db = getdb()
    INTERVAL = 7

    animals = [r['animal'] for r in
               db.query("""SELECT animal FROM animal """
                        """ WHERE animal NOT LIKE '%test%' """)]
    for a in animals:
        rs = db.query("""SELECT * FROM session WHERE """
                      """  animal='%s' AND """
                      """  restricted=1 AND tested=1 """
                      """  AND water_work > 0 AND water_work IS NOT NULL """
                      """  AND weight IS NOT NULL """
                      """  ORDER BY date """ % (a,))

        for n in range(len(rs)):
            v = []
            if n >= INTERVAL:
                for k in range(INTERVAL):
                    v.append(rs[n-k-1]['water_work']/rs[n-k-1]['weight'])
            v = np.array(v)

            # over PREVIOUS 7 testing days
            # dtb is ml/kg, clipped to 10 ml/kg
            # dtb_ml is ml's min vol animal should get today..
            dtb = round(max(10.0, np.mean(v) - (2 * np.std(v))))
            dtb_ml = round(dtb * rs[n]['weight'])
            xdtb = round(max(0.0, np.mean(v) - (2 * np.std(v))))
            xdtb_ml = round(dtb * rs[n]['weight'])
            
            print a, rs[n]['date'], dtb, dtb_ml, xdtb, xdtb_ml


"""
Failure modes:

- water_work == 0 -- this is usually because tested should be unchecked!
     ... water_work > 0 AND water_work IS NOT NULL ...
- no weight entered on a work day..     

"""            
