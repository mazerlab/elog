#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

# initial tables for log management

import sys
from tools import *

def askyn(msg):
    sys.stderr.write(msg + ' [yN]: ')
    l = sys.stdin.readline()
    if l[0] == 'y' or l[0] == 'Y':
        return 1
    else:
        return 0

def init_session(db):
    return db.query("""
    CREATE TABLE session
    (
    sessionID     INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE KEY,
    animal     CHAR(10),
    user       VARCHAR(10),
    computer   VARCHAR(40),
    date       DATE,
    restricted INT,
    tested     INT,
    water_work INT,
    water_sup  INT,
    fruit      VARCHAR(255),
    food       INT,
    weight     DOUBLE,
    thweight   DOUBLE,
    ntrials     INT,
    ncorrect    INT,
    health_stool INT,
    health_urine INT,
    health_skin  INT,
    health_pcv  INT,
    ncorrect    INT,
    note       TEXT,
    locked     INT,
    tags       VARCHAR(1024),
    lastmod    VARCHAR(255)
    )
    """)

def init_exper(db):
    return db.query("""
    CREATE TABLE exper
    (
    experID     INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE KEY,
    exper       CHAR(10),
    animal      CHAR(10),
    dir         VARCHAR(255),
    date        DATE,
    time        VARCHAR(11),
    note        TEXT,
    locked      INT,
    deleted     INT,
    tags       VARCHAR(1024),
    lastmod     VARCHAR(255),
    )
    """)

def init_unit(db):
    return db.query("""
    CREATE TABLE unit
    (
    unitID      INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE KEY,
    experID     INT UNSIGNED,
    exper       char(10),
    unit        CHAR(10),
    animal      CHAR(10),
    date        DATE,
    well        VARCHAR(11),
    wellloc     VARCHAR(255),
    area        VARCHAR(10),
    depth       INT,
    qual        FLOAT,
    rfx         FLOAT,
    rfy         FLOAT,
    rfr         FLOAT,
    latency     FLOAT,
    ori         FLOAT,
    color       VARCHAR(20),
    crap        INT,
    note        TEXT,
    locked      INT,
    tags        VARCHAR(1024),
    lastmod     VARCHAR(255)
    )
    """)
    
def init_dfile(db):
    return db.query("""
    CREATE TABLE dfile
    (
    dfileID  INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE KEY,
    exper    CHAR(10),
    animal   CHAR(10),
    date     DATE,
    user     CHAR(10),
    src      VARCHAR(255) UNIQUE,
    filetype CHAR(20),
    latency  FLOAT,
    winsize  FLOAT,
    crap     INT,
    preferred INT,
    note     TEXT,
    locked   INT,
    tags     VARCHAR(1024),
    lastmod  VARCHAR(255)
    )
    """)

def init_attachment(db):
    return db.query("""
    CREATE TABLE attachment
    (
    attachmentID     INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE KEY,
    title      VARCHAR(255),
    user       VARCHAR(10),
    date       DATE,
    type       VARCHAR(255),
    note       TEXT,
    srctable   varchar(20),
    srcID      INT UNSIGNED NOT NULL,
    
    data       LONGBLOB,

    locked     INT,
    tags       VARCHAR(1024),
    lastmod    VARCHAR(255)
    )
    """)

def init_empty_db(host=None):
    db = Database(host=host)
    if db.connection is None:
        return
    
    if db.query("CREATE DATABASE %s" % db.db) is None:
        print "database '%s' exists" % db.db
        if askyn('  drop it?'):
            print "%s: making new database (and tables)" % db.db
            db.query("DROP DATABASE %s" % db.db)
            db.query("CREATE DATABASE %s" % db.db)
        else:
            print "%s: using existing database" % db.db
        db.query("use %s" % db.db)

    if init_session(db) is None:
        print "%s: table 'session' already exists" % db.db
        if askyn('  drop it?'):
            db.query("DROP TABLE session")
            init_session(db)
            
    if init_exper(db) is None:
        print "%s: table 'exper' already exists" % db.db
        if askyn('  drop it?'):
            db.query("DROP TABLE exper")
            init_exper(db)
        
    if init_unit(db) is None:
        print "%s: table 'unit' already exists" % db.db
        if askyn('  drop it?'):
            db.query("DROP TABLE unit")
            init_unit(db)

    if init_dfile(db) is None:
        print "%s: table 'dfile' already exists" % db.db
        if askyn('  drop it?'):
            db.query("DROP TABLE dfile")
            init_dfile(db)

    if init_attachment(db) is None:
        print "%s: table 'attachment' already exists" % db.db
        if askyn('  drop it?'):
            db.query("DROP TABLE attachment")
            init_attachment(db)

    db.close()
    

if __name__ == '__main__':
    init_empty_db()
