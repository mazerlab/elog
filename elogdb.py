#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

# DB object for elog scripts

import MySQLdb

class DB:
    host='sql.mlab.yale.edu'
    user='dbusernopass'
    passwd=''
    db='mlabdata'

    def __init__(self):

        self.connection = MySQLdb.connect(DB.host,
                                          DB.user,
                                          DB.passwd,
                                          DB.db)
        self.cursor = self.connection.cursor()

    def row2dict(self, descr, row):
        """
        Convert a SQL query result-row into a dictionary.
        """
        dict = {}
        for k in range(len(descr)):
            if row[k] is None:
                dict[descr[k][0]] = ''
            else:
                dict[descr[k][0]] = row[k]
        return dict

    def q(self, cmd, one=False):
        try:
            self.cursor.execute(cmd)
            descr = self.cursor.description
            if not one:
                rows = self.cursor.fetchall()
                dicts = []
                for row in rows:
                    dicts.append(self.row2dict(descr, row))
                return (1, dicts)
            else:
                row = self.cursor.fetchone()
                return (1, row)

        except MySQLdb.Error, e:
            (number, msg) = e.args
            return (None, e)
