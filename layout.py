#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

from tools import *

# Fields here are:
#   Name PmwType PythonValidationFn ReadOnly Width (row, col, colspan)
# Everything after PythonValidFn is optional.. if anything in table
# has (row,col..), everything must!

SESSION_FIELDS = (
    # sessionID
    ("animal",          None, None, DISABLED, 10,  (0, 0, 1), None),
    ("date",            None, sdate, DISABLED, 12, (1, 0, 1), None),
    ("user",            None, None, NORMAL, 10,    (2, 0, 1), None),
    ("computer",        None, None, NORMAL, 10,    (3, 0, 1), None),

    ("restricted",      BOOL, int, NORMAL, 1,      (0, 1, 1), None),
    ("tested",          BOOL, int, NORMAL, 1,      (1, 1, 1), None),
    ("ncorrect",        INTEGER, int, NORMAL, 5,   (2, 1, 1), None),
    ("ntrials",         INTEGER, int, NORMAL, 5,   (3, 1, 1), None),
    
    ("water_work (ml)", INTEGER, int, NORMAL, 5,    (0, 2, 1), None),
    ("water_sup (ml)",  INTEGER, int, NORMAL, 5,    (1, 2, 1), None),
    ("dtb (ml/kg)",     REAL,  float, DISABLED, 5,  (2, 2, 1), None),
    ("dtb_ml",          REAL,  float, DISABLED, 5,  (3, 2, 1), None),

    ("fruit",           None, None, NORMAL, 10,    (0, 3, 1), None),
    ("fruit_ml",        INTEGER, int, NORMAL, 5,   (1, 3, 1), None),
    ("totalfluid (ml)", REAL, float, DISABLED, 5,  (2, 3, 1), None),
    ("food",            INTEGER, int, NORMAL, 5,   (3, 3, 1), None),
    
    ("weight (kg)",     REAL, float, NORMAL, 5,    (0, 4, 1), None),
    ("thweight (kg)",   REAL, float, NORMAL, 5,    (1, 4, 1), None),
    ("xdtb (ml/kg)", REAL,  float, DISABLED, 5,  (2, 4, 1), None),
    ("xdtb_ml (ml)", REAL,  float, DISABLED, 5,  (3, 4, 1), None),

    ("note",            TEXT, None, NORMAL, (90, 20), (4, 0, 5), None),
    )

EXPER_FIELDS = (
    # experID
    ("exper",           None, None, DISABLED, 10,      (0, 0, 1), None),
    ("animal",          None, None, DISABLED, 10,      (0, 1, 1), None),
    ("date",            None, sdate, DISABLED, 12,      (0, 2, 1), None),
    ("time",            None, None, NORMAL, 21,      (0, 3, 1), None),
    ("deleted",         BOOL, int, NORMAL, 0,        (0, 4, 1), None),
    ("note",            TEXT, None, NORMAL, (80, 10),    (1, 0, 4), None),
    )

UNIT_FIELDS = (
    # unitID
    ("unit",            None, None, DISABLED, 10,      (0, 0, 1), None),
    ("exper",           None, None, DISABLED, 10,      (1, 0, 1), None),
    ("animal",          None, None, DISABLED, 10,      (2, 0, 1), None),
    ("date",            None, sdate, DISABLED, 12,      (3, 0, 1), None),

    ("well",            None, None, NORMAL, 5,       (0, 1, 1), None),
    ("wellloc",         None, None, NORMAL, 10,      (1, 1, 1), None),
    ("area",            None, None, NORMAL, 10,      (2, 1, 1), None),
    ("hemi",            None, None, NORMAL, 2,      (3, 1, 1), None),
    
    ("depth",           INTEGER, int, NORMAL, 10,  (0, 2, 1), None),
    ("qual",            REAL, float, NORMAL, 10,   (1, 2, 1), None),
    ("ori",             REAL, float, NORMAL, 10,   (2, 2, 1), None),
    ("color",           None, None, NORMAL, 15,      (3, 2, 1), None),
    
    ("rfx",             REAL, float, NORMAL, 10,   (0, 3, 1), None),
    ("rfy",             REAL, float, NORMAL, 10,   (1, 3, 1), None),
    ("rfr",             REAL, float, NORMAL, 10,   (2, 3, 1), None),
    ("latency",         REAL, float, NORMAL, 10,   (3, 3, 1), None),
    
    ("crap",            BOOL, int, NORMAL, 0,      (0, 4, 1), None),
    
    ("note",            TEXT, None, NORMAL, (80,3),      (5, 0, 4), None),
    )

DFILE_FIELDS = (
    # dfileID
    ("exper",           None, None, DISABLED, 10,     (0, 0, 1), None),
    ("animal",          None, None, DISABLED, 10,     (0, 1, 1), None),
    ("date",            None, sdate, DISABLED, 12,    (0, 2, 1), None),
    
    ("filetype",        None, None, DISABLED, 10,     (1, 0, 1), None),
    ("latency",         REAL, float, NORMAL, 1,       (1, 1, 1), None),
    ("winsize",         REAL, float, NORMAL, 1,       (1, 2, 1), None),

    ("crap",            BOOL, int, NORMAL, 1,         (0, 3, 1), None),
    ("preferred",       BOOL, int, NORMAL, 1,         (1, 3, 1), None),
    
    ("src",             None, None, DISABLED, 80,     (3, 0, 3), None),
    ("note",            TEXT, None, NORMAL, (80,3),    (4, 0, 3), None),
    )

ATTACHMENT_FIELDS = (
    # attachmentID
    ("title",          None, None, NORMAL, 40,       (0, 0, 1), None),
    ("user",           None, None, DISABLED, 10,     (0, 1, 1), None),
    ("date",           None, None, DISABLED, 12,     (0, 2, 1), None),
    ("type",           None, sdate, DISABLED, 12,    (0, 3, 1), None),
    ("note",           TEXT, None, NORMAL, (80,4),   (1, 0, 4), None),
    )

