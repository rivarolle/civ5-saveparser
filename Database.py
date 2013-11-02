import sqlite3

__author__ = "Hussein Kaddoura"
__copyright__ = "Copyright 2013, Hussein Kaddoura"
__credits__ = ["Hussein Kaddoura" ]
__license__ ="MIT"
__version__ = "0.1"
__maintainer__ = "Hussein Kaddoura"
__email__ = "hussein.nawwaf@gmail.com"
__status__="Development"


class SqliteReader:
    def __init__(self, dbName):
        self.conn = sqlite3.connect(dbName)

    def __enter__(self):
        return self;

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def fetchOne(self, sql, t):
        c = self.conn.cursor()
        c.execute(sql, t)
        return c.fetchone()