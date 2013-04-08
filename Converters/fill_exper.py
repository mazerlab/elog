#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
This script extracts data from the note fields in the
NOTE table inserts them info the EXPER and UNIT tables.

The NOTE table should be initialized 1st using fill_notes.py.
"""

import string, sys, re

from elogtools import *
from keyboard import keyboard
from time import strptime

BADFLOAT = -1.0e6

db = Database()
(ok, rows) = db.query("""SELECT note FROM note WHERE 1""")

def safeconv(s, converter, errval):
    try:
        return converter(s)
    except ValueError:
        return errval

for row in rows:
    if string.find(row['note'], 'TIME:') < 0:
        continue;

    TIME = re.findall('TIME: .*$', row['note'], re.MULTILINE)
    DATE = re.findall('DATE: .*$', row['note'], re.MULTILINE)
    CELL = re.findall('CELL: .*$', row['note'], re.MULTILINE)
    AREA = re.findall('AREA: .*$', row['note'], re.MULTILINE)
    DEPTH = re.findall('DEPTH: .*$', row['note'], re.MULTILINE)
    QUAL = re.findall('QUAL: .*$', row['note'], re.MULTILINE)
    RF = re.findall('RF: .*$', row['note'], re.MULTILINE)
    PPD = re.findall('PPD: .*$', row['note'], re.MULTILINE)
    ORI = re.findall('ORI: .*$', row['note'], re.MULTILINE)
    COLOR = re.findall('COLOR: .*$', row['note'], re.MULTILINE)

    if 1:
        NOTE = []
        n = row['note']
        n1 = 0
        for k in range(len(TIME)):
            n1 = string.find(n, 'NOTES:', n1)
            n2 = string.find(n, '\n   TIME:', n1)
            if n2 < 0:
                n2 = len(n)
            t = n[(n1+8):(n2-1)]
            NOTE.append(t)
            n1 = n2

    if 0:
        start = 0
        NOTE = []
        REST = []
        for k in range(len(TIME)):
            n1 = string.find(row['note'], '  NOTES:', start)
            n2 = string.find(row['note'], '  FILES:', n1)
            NOTE.append(string.strip(row['note'][(n1+len('  NOTES:')):n2]))
            r = row['note'][n2:]
            r = string.replace(r, '  FILES:', '')
            ix = string.find(r, '\n\n')
            if ix < 0:
                ix = len(r)
            r = string.replace(r, '\n\t\t', '\n')
            # replace dfile names with "links"
            REST.append(re.sub('([a-z]*[0-9][0-9][0-9][0-9]\..*\.[0-9][0-9][0-9])',
                               '{dfile:\\1}', r))
            start = n2

    for k in range(len(TIME)):
        cell = string.split(CELL[k])[1]
        time = string.join(string.split(TIME[k])[1:])
        date = string.join(string.split(DATE[k])[1:])
        try:
            date = strptime(date,'%Y-%m-%d')
        except ValueError:
            try:
                date = strptime(date,'%d-%b-%Y')
            except ValueError:
                try:
                    date = strptime(date,'%m/%d/%Y')
                except ValueError:
                    print DATE[k],date
                    date = (1999, 01, 01)
        date = "%04d-%02d-%02d" % (date[0],date[1],date[2])
        animal = animals[cell[:-4]]
        area = string.join(string.split(AREA[k])[1:])

        depth = string.replace(DEPTH[k], 'um', ' um')
        try:
            depth = int(string.split(depth)[1])
        except ValueError:
            depth = -1
        qual = string.join(string.split(QUAL[k])[1:])
        if qual == 'MU':
            qual = 0
        else:
            qual = string.split(qual, '/')[0]
            qual = safeconv(qual, float, -1.0)
        rf = string.join(string.split(RF[k])[1:])
        pos = string.split(string.split(rf)[0][1:-1], ',')
        try:
            rfx = safeconv(pos[0], float, BADFLOAT)
            rfy = safeconv(pos[1], float, BADFLOAT)
            rfr = safeconv(string.split(rf)[1][2:], float, BADFLOAT)
        except:
            rfx, rfy, rfr = BADFLOAT, BADFLOAT, BADFLOAT
        #ppd = string.join(string.split(PPD[k])[1:])
        
        ori = string.replace(ORI[k], 'deg', '')
        ori = safeconv(string.join(string.split(ori)[1:]), float, BADFLOAT)
        try:
            color = string.join(string.split(COLOR[k])[1:])
        except:
            color = '??'
        #note = NOTE[k]+'\n'+REST[k]
        note = NOTE[k]

        exper = cell
        unit = 'TTL'

        (ok, r) = db.query("""
        SELECT experID FROM exper WHERE exper='%s'
        """ % exper)
        if len(r) > 0:
            (ok, e) = db.exe("""
            REPLACE INTO exper
            (experID, exper, animal, date, time, note)
            VALUES %s
            """ % ( (int(r[0]['experID']), exper, animal, date, time, note), ))
        else:
            (ok, e) = db.exe("""
            INSERT INTO exper
            (exper, animal, date, time, note)
            VALUES %s
            """ % ( (exper, animal, date, time, note), ))

        (ok, r) = db.query("""
        SELECT unitID FROM unit
        WHERE animal='%s' AND date='%s' AND exper='%s' AND unit='TTL'
        """ % (animal, date, exper))
        if len(r) >0:
            (ok, e) = db.exe("""
            REPLACE INTO unit
            (unitID,
            exper, unit, animal, date,
            area, depth, qual,
            rfx, rfy, rfr, ori, color)
            VALUES %s
            """ % ( (int(r[0]['unitID']),
                     exper, unit, animal, date,
                     area, depth, qual,
                     rfx, rfy, rfr, ori, color), ))
        else:
            (ok, e) = db.exe("""
            INSERT INTO unit
            (exper, unit, animal, date,
            area, depth, qual,
            rfx, rfy, rfr, ori, color)
            VALUES %s
            """ % ( (exper, unit, animal, date,
                     area, depth, qual,
                     rfx, rfy, rfr, ori, color), ))

            
(ok, e) = db.exe("""UPDATE unit SET depth=NULL WHERE depth=-1""")
(ok, e) = db.exe("""UPDATE unit SET qual=NULL WHERE qual=-1""")
(ok, e) = db.exe("""UPDATE unit SET ori=NULL WHERE ori=-1e6""")
(ok, e) = db.exe("""UPDATE unit SET rfx=NULL WHERE rfx=-1e6""")
(ok, e) = db.exe("""UPDATE unit SET rfy=NULL WHERE rfy=-1e6""")
(ok, e) = db.exe("""UPDATE unit SET rfr=NULL WHERE rfr=-1e6""")

db.close()

