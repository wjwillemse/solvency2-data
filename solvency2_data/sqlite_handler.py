"""
This module contains all the handler functions for the sqlite database storing the data
"""
import os
import sqlite3
from sqlite3 import Error


class EiopaDB(object):
    def __init__(self, database):
        self.database = database
        if not os.path.isfile(database):
            root_folder = os.path.dirname(database)
            if not os.path.exists(root_folder):
                os.makedirs(root_folder)
            create_eiopa_db(database)
        self.set_conn()
        print('DB initialised')

    def reset(self):
        """ Hard reset of the database """
        if os.path.exists(self.database):
            self._close_conn()
            os.remove(self.database)
        create_eiopa_db(self.database)
        self.set_conn()

    def set_conn(self):
        self.conn = create_connection(self.database)

    def _close_conn(self):
        if self.conn is not None:
            self.conn.close()

    def get_set_id(self, url):
        """
        Get the url id for a url
        If not there, check if valid then add
        """
        cur = self.conn.cursor()
        try:
            set_id = cur.execute("SELECT url_id FROM catalog WHERE url = '" + url + "'").fetchone()
        except Error:
            pass
        if set_id is not None:
            set_id = set_id[0]  # Cursor returns a tuple and only want id
        else:
            set_id = self._add_set(url)
        return set_id

    def _add_set(self, url):
        """ Private method, only called when url not already in catalog """
        sql = "INSERT INTO catalog (url) VALUES ('" + url + "')"
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.lastrowid


def create_connection(database):
    """ create a database connection to the SQLite database
        specified by database file path
    :param database: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        print(e)

    return conn


def exec_sql(conn, sql):
    """ Execute sql in connection """
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def create_eiopa_db(database=r"eiopa.db"):
    table_def = {
        'catalog':
            """ CREATE TABLE IF NOT EXISTS catalog (
                                     url_id INTEGER NOT NULL PRIMARY KEY,
                                     url TEXT
                                     ); """,
        'rfr':
            """ CREATE TABLE IF NOT EXISTS rfr_raw (
                                     url_id INTEGER NOT NULL,
                                     ref_date TEXT,
                                     scenario TEXT,
                                     currency_code TEXT,
                                     duration INTEGER,
                                     spot REAL,
                                     FOREIGN KEY (url_id) REFERENCES catalog (url_id)
                                        ON DELETE CASCADE ON UPDATE NO ACTION
                                     ); """,
        'spreads':
            """CREATE TABLE IF NOT EXISTS spreads_raw (
                                        url_id INTEGER NOT NULL,
                                        ref_date TEXT,
                                        type TEXT,
                                        currency_code TEXT,
                                        duration INTEGER,
                                        cc_step INTEGER,
                                        spread REAL,
                                        FOREIGN KEY (url_id) REFERENCES catalog (url_id)
                                        ON DELETE CASCADE ON UPDATE NO ACTION
                                        );""",
        'govies':
            """CREATE TABLE IF NOT EXISTS govies_raw (
                                            url_id INTEGER NOT NULL,
                                            ref_date TEXT,
                                            country_code TEXT,
                                            duration INTEGER,
                                            spread REAL,
                                            FOREIGN KEY (url_id) REFERENCES catalog (url_id)
                                        ON DELETE CASCADE ON UPDATE NO ACTION
                                            );"""
    }

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create tables
        for key, val in table_def.items():
            exec_sql(conn, val)
    else:
        print("Error! cannot create the database connection.")


