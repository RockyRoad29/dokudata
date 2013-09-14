import os
import re
import sqlite3
from dokunamespace import DokuNamespace
from dokutree import DokuPages, DokuMedia, DokuAttic, DokuMediaAttic


class Doku:
    """A dokuwiki site, from host's point of view.
    """
    #: Database definition script
    ddl = '''
    CREATE TABLE nodes (
            id integer primary key autoincrement,
            type varchar(10) not null,
            ns_id integer references ns(id),
            name varchar(255) not null,
            size integer);
    CREATE TABLE ns (
            id integer primary key autoincrement,
            fullname varchar(255) unique not null);
    CREATE TABLE revisions (
            id integer primary key autoincrement,
            node_id integer references nodes(id),
            time varchar(255) not null,
            size integer);
    '''


    def __init__(self, path):
        self.path = path
        self.version = None
        self.data = os.path.join(self.path, "data")
        self.namespaces = [DokuNamespace("", parent=None, data=self.data)]

    def load(self):
        """Scans a directory tree and builds site structure"""
        root = self.namespaces[0]
        DokuPages(self).load(None, root)
        DokuMedia(self).load(None,root)
        DokuAttic(self).load(None,root)
        DokuMediaAttic(self).load(None,root)

    def summary(self):
        root = self.namespaces[0]
        root.summary()


    def create_database(self, db, overwrite=False):
        """ Create database tables.
        :param db:
        :param overwrite:

        >>> conn = Doku("").create_database("/tmp/test.db", overwrite=True)
        >>> conn.cursor().execute("select count(*) from nodes").fetchone()[0]
        0
        """
        if os.path.exists(db):
            if overwrite:
                os.unlink(db)
            else:
                raise FileExistsError("I cannot reuse an existing database")

        conn = sqlite3.connect(db)

        c = conn.cursor()
        c.executescript(Doku.ddl)

        conn.commit()
        return conn

    def persist2db(self, db, overwrite=False):
        conn = self.create_database(db, overwrite)
        c = conn.cursor()
        root = self.namespaces[0]
        root.persist2db(c)
        # Save (commit) the changes
        conn.commit()


        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        conn.close()


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
