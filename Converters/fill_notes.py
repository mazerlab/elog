#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
This script extracts data from a standard textfile log and
inserts it into the SQL database.
"""

import MySQLdb, string, sys

test = 0

def nullify(s, fmt):
    if s is None:
        return "NULL"
    elif fmt == "%s":
        return "'"+s+"'"
    else:
        return s
    

import elogtools
db = elogtools.Database()
(conn, c) = (db.connection, db.cursor)

d = None
nl = 0
note = ''
who = 'ND'
computer = 'ND'
biscs = -1
while 1:
    l = sys.stdin.readline()
    orig = l[:]
    nl = nl + 1

    if (l[0:5] == "----") or (len(l) == 0):
        if d is None:
            note = ''
            continue
        if len(note) > 0 and note[0] == '\n':
            note = note[1:]
        note = string.replace(note, '"', "'")

        cmd = """
        INSERT INTO note (date,animal,user,computer,restricted,tested,
                water_work,water_sup,fruit,weight,food,note)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "%s")
        """ % (nullify(d, '%s'),
               nullify(sys.argv[1], '%s'),
               nullify(who, '%s'),
               nullify(computer, '%s'),
               'NULL',
               'NULL',
               nullify(w1, '%f'),
               nullify(w2, '%f'),
               nullify(fruit, '%s'),
               nullify(wt, '%f'),
               nullify(biscs, '%d'),
               note)

        if not test:
            c.execute(cmd)
        if len(l) is 0:
            break
        d = None
        who = None
        computer = None
        w1 = None
        w2 = None
        fruit = None
        biscs = None
        wt = None
        note = ''
    elif l[0:5] == 'DATE:':
        d = string.split(l)[1]
    elif l[0:5] == ' WHO:':
        who = string.split(l)[1]
        x = string.split(who, '@')
        if len(x) > 1:
            who = x[0]
            computer = x[1]
        else:
            computer = 'ND'
    elif l[0:5] == ' H2O:':
        w1 = None
        w2 = None
        fruit = None
        biscs = None
        try:
            l = string.replace(l, 'H2O:', 'H2O: ')
            l = string.replace(l, '/ ', '/')
            l = string.replace(l, 'ml', ' ml')
            l = string.replace(l, 'ad libitum', '99999')
            l = string.replace(l, 'lixit/yarc', '99999')
            l = string.replace(l, '~', '')
            l = string.replace(l, '>', '')
            if string.find(l, '[rew/supp  ml + fruit]') >= 0:
                l = string.replace(l, '[rew/supp  ml + fruit]', 'ND')
            x = string.replace(string.split(l)[1], '/', '+')
            x = string.split(x, '+')
            offset = 0
            if x is 'ml':
                w1 = None
                w2 = None
                offset = -1
            elif len(x) == 2:
                w1 = int(x[0])
                w2 = int(x[1])
            else:
                w1 = int(x[0])
                w2 = 0
            if string.find(l, 'DB') < 0:
                fruit = string.join(string.split(l)[(4+offset):])
                biscs = None
            else:
                fruit = string.join(string.split(l)[(4+offset):-3])
                biscs = int(string.split(l)[-2])
        except:
            sys.stderr.write('h2o error, line %d: %s --> %s\n' % \
            (nl, orig[:-1], (w1,w2,fruit,biscs)))
    elif l[0:5] == '  WT:':
        wt = None
        l = string.replace(l, 'SB', 'DB')
        try:
            wt = float(string.split(l)[1])
        except:
            sys.stderr.write('weight error, line %d: %s --> %s\n' % \
            (nl, orig[:-1], (wt,)))
    else:
        note = note + l

db.close()


