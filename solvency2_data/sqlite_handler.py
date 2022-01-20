"""
This module contains all the handler functions for the sqlite database storing the data
"""
import os
import sqlite3
from sqlite3 import Error
import logging


class EiopaDB(object):
    """
    Database object to store the eiopa data

    """
    def __init__(self, database):
        """
        Initialize database

        Args:
            database: database specified by database file path
    
        Returns:
            None

        """
        self.database = database
        if not os.path.isfile(database):
            root_folder = os.path.dirname(database)
            if not os.path.exists(root_folder):
                os.makedirs(root_folder)
            create_eiopa_db(database)
        self.set_conn()
        logging.info("DB initialised")

    def reset(self):
        """
        Hard reset of the database

        Args:
            None
    
        Returns:
            None

        """
        if os.path.exists(self.database):
            self._close_conn()
            os.remove(self.database)
        create_eiopa_db(self.database)
        self.set_conn()

    def set_conn(self):
        """
        Set database connection

        Args:
            None
    
        Returns:
            None

        """
        self.conn = create_connection(self.database)

    def _close_conn(self):
        """
        Close database connection

        Args:
            None
    
        Returns:
            None

        """
        if self.conn is not None:
            self.conn.close()

    def get_set_id(self, url):
        """
        Get the url id for a url
        If not there, check if valid then add

        Args:
            url: url to be found
    
        Returns:
            None

        """
        cur = self.conn.cursor()
        try:
            set_id = cur.execute(
                "SELECT url_id FROM catalog WHERE url = '" + url + "'"
            ).fetchone()
        except Error:
            pass
        if set_id is not None:
            set_id = set_id[0]  # Cursor returns a tuple and only want id
        else:
            set_id = self._add_set(url)
        return set_id

    def _add_set(self, url):
        """Private method, only called when url not already in catalog"""
        sql = "INSERT INTO catalog (url) VALUES ('" + url + "')"
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.lastrowid

    def update_catalog(self, url_id: int, dict_vals: dict):
        set_lines = ", ".join([f"{k}='{v}'" for k, v in dict_vals.items()])
        sql = "UPDATE catalog SET %s WHERE url_id=%s" % (set_lines, url_id)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()


def create_connection(database: str):
    """
    create a database connection to the SQLite database

    Args:
        database: database specified by database file path

    Returns:
        connection object or None
    
    """
    conn = None
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        logging.error(e)

    return conn


def exec_sql(conn, sql: str):
    """
    Execute sql in connection

    Args:
        conn: database connection
        sql: sql statement to be executed

    Returns:
        None

    """

    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        logging.error(e)


def create_eiopa_db(database: str = r"eiopa.db") -> None:
    """
    Create the EIOPA database

    Args:
        database: name of the database to be created

    Returns:
        None
    """
    table_def = {
        "catalog": """ CREATE TABLE IF NOT EXISTS catalog (
                                     url_id INTEGER NOT NULL PRIMARY KEY,
                                     url TEXT,
                                     set_type TEXT,
                                     primary_set BOOLEAN,
                                     ref_date TEXT
                                     ); """,
        "meta": """ CREATE TABLE IF NOT EXISTS meta (
                                     url_id INTEGER NOT NULL,
                                     ref_date TEXT,
                                     Country TEXT,
                                     Info TEXT,
                                     Coupon_freq INTEGER,
                                     LLP INTEGER,
                                     Convergence INTEGER,
                                     UFR REAL,
                                     alpha REAL,
                                     CRA REAL,
                                     VA REAL,
                                     FOREIGN KEY (url_id) REFERENCES catalog (url_id)
                                        ON DELETE CASCADE ON UPDATE NO ACTION
                                     ); """,
        "rfr": """ CREATE TABLE IF NOT EXISTS rfr (
                                     url_id INTEGER NOT NULL,
                                     ref_date TEXT,
                                     scenario TEXT,
                                     currency_code TEXT,
                                     duration INTEGER,
                                     spot REAL,
                                     FOREIGN KEY (url_id) REFERENCES catalog (url_id)
                                        ON DELETE CASCADE ON UPDATE NO ACTION
                                     ); """,
        "spreads": """CREATE TABLE IF NOT EXISTS spreads (
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
        "govies": """CREATE TABLE IF NOT EXISTS govies (
                                            url_id INTEGER NOT NULL,
                                            ref_date TEXT,
                                            country_code TEXT,
                                            duration INTEGER,
                                            spread REAL,
                                            FOREIGN KEY (url_id) REFERENCES catalog (url_id)
                                        ON DELETE CASCADE ON UPDATE NO ACTION
                                            );""",
        "sym_adj": """CREATE TABLE IF NOT EXISTS sym_adj (
                                    url_id INTEGER NOT NULL,
                                    ref_date TEXT,
                                    sym_adj REAL,
                                    FOREIGN KEY (url_id) REFERENCES catalog (url_id)
                                ON DELETE CASCADE ON UPDATE NO ACTION
                                    );""",
    }
    # create a database connection
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # create tables
        for key, val in table_def.items():
            exec_sql(conn, val)
    else:
        logging.error("Error! cannot create the database connection.")
