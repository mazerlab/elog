#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

from tools import *

# Fields here are:
#   Name PmwType PythonValidationFn ReadOnly Width (row, col, colspan)
# Everything after PythonValidFn is optional.. if anything in table
# has (row,col..), everything must!

SESSION_FIELDS = (
    # sessionID
    ("animal",          None, None, DISABLED, 10,      (0, 0, 1), ),
    ("user",            None, None, NORMAL, 10,      (1, 0, 1), ),
    ("restricted",      BOOL, int, NORMAL, 0,      (2, 0, 1), ),
    
    ("date",            None, sdate, DISABLED, 12,      (0, 1, 1), ),
    ("computer",        None, None, NORMAL, 10,      (1, 1, 1), ),
    ("tested",          BOOL, int, NORMAL, 0,      (2, 1, 1), ),
    
    ("water_work",      INTEGER, int, NORMAL, 10,  (0, 3, 1), ),
    ("water_sup",       INTEGER, int, NORMAL, 10,  (1, 3, 1), ),
    ("fruit",           None, None, NORMAL, 0,       (2, 3, 1), ),

    ("food",            INTEGER, int, NORMAL, 5,   (0, 4, 1), ),
    ("weight",          REAL, float, NORMAL, 5,    (1, 4, 1), ),
    ("thweight",        REAL, float, NORMAL, 5,    (2, 4, 1), ),

    ("ncorrect",        INTEGER, int, NORMAL, 5,   (3, 0, 1), ),
    ("ntrials",         INTEGER, int, NORMAL, 5,   (3, 1, 1), ),
    
    ("note",            TEXT, None, NORMAL, (90, 20), (4, 0, 5), ),
    )

EXPER_FIELDS = (
    # experID
    ("exper",           None, None, DISABLED, 10,      (0, 0, 1), ),
    ("animal",          None, None, DISABLED, 10,      (0, 1, 1), ),
    ("date",            None, sdate, DISABLED, 12,      (0, 2, 1), ),
    ("time",            None, None, NORMAL, 21,      (0, 3, 1), ),
    ("deleted",         BOOL, int, NORMAL, 0,        (0, 4, 1), ),
    ("note",            TEXT, None, NORMAL, (80, 10),    (1, 0, 4), ),
    )

UNIT_FIELDS = (
    # unitID
    ("unit",            None, None, DISABLED, 10,      (0, 0, 1), ),
    ("exper",           None, None, DISABLED, 10,      (1, 0, 1), ),
    ("animal",          None, None, DISABLED, 10,      (2, 0, 1), ),
    ("date",            None, sdate, DISABLED, 12,      (3, 0, 1), ),

    ("well",            None, None, NORMAL, 5,       (0, 1, 1), ),
    ("wellloc",         None, None, NORMAL, 10,      (1, 1, 1), ),
    ("area",            None, None, NORMAL, 10,      (2, 1, 1), ),
    ("hemi",            None, None, NORMAL, 2,      (3, 1, 1), ),
    
    ("depth",           INTEGER, int, NORMAL, 10,  (0, 2, 1), ),
    ("qual",            REAL, float, NORMAL, 10,   (1, 2, 1), ),
    ("ori",             REAL, float, NORMAL, 10,   (2, 2, 1), ),
    ("color",           None, None, NORMAL, 15,      (3, 2, 1), ),
    
    ("rfx",             REAL, float, NORMAL, 10,   (0, 3, 1), ),
    ("rfy",             REAL, float, NORMAL, 10,   (1, 3, 1), ),
    ("rfr",             REAL, float, NORMAL, 10,   (2, 3, 1), ),
    ("latency",         REAL, float, NORMAL, 10,   (3, 3, 1), ),
    
    ("crap",            BOOL, int, NORMAL, 0,      (0, 4, 1), ),
    
    ("note",            TEXT, None, NORMAL, (80,3),      (5, 0, 4), ),
    )

DFILE_FIELDS = (
    # dfileID
    ("exper",           None, None, DISABLED, 10,     (0, 0, 1), ),
    ("animal",          None, None, DISABLED, 10,     (0, 1, 1), ),
    ("date",            None, sdate, DISABLED, 12,    (0, 2, 1), ),
    
    ("filetype",        None, None, DISABLED, 10,     (1, 0, 1), ),
    ("latency",         REAL, float, NORMAL, 1,       (1, 1, 1), ),
    ("winsize",         REAL, float, NORMAL, 1,       (1, 2, 1), ),

    ("crap",            BOOL, int, NORMAL, 1,         (0, 3, 1), ),
    ("preferred",       BOOL, int, NORMAL, 1,         (1, 3, 1), ),
    
    ("src",             None, None, DISABLED, 80,     (3, 0, 3), ),
    ("note",            TEXT, None, NORMAL, (80,3),    (4, 0, 3), ),
    )

ATTACHMENT_FIELDS = (
    # attachmentID
    ("title",          None, None, NORMAL, 40,       (0, 0, 1), ),
    ("user",           None, None, DISABLED, 10,     (0, 1, 1), ),
    ("date",           None, None, DISABLED, 12,     (0, 2, 1), ),
    ("type",           None, sdate, DISABLED, 12,    (0, 3, 1), ),
    ("note",           TEXT, None, NORMAL, (80,4),   (1, 0, 4), ),
    )

