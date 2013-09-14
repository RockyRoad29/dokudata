import logging
import os
import re
from checkbox.properties import File
import sqlite3


class Doku:
    """A dokuwiki site, from host's point of view.

    Class attributes
    ----------------

    attic_pattern - Page attic filename pattern.

    >>> m = Doku.attic_pattern.match("calendrier.1367320658.txt.gz")
    >>> [m.group(i) for i in (1, 2, 3)]
    ['calendrier', '1367320658', '']

    #: media_attic_pattern - Media attic filename pattern

    #
    >>> m = Doku.media_attic_pattern.match("fiche_inscription_v1.1336687823.pdf")
    >>> [m.group(i) for i in (1, 2, 3)]
    ['fiche_inscription_v1', '1336687823', '.pdf']
    """
    #: Page attic filename pattern.
    attic_pattern = re.compile('^(.*)\.([0-9]+)()\.txt\.gz')
    #: Media attic filename pattern
    media_attic_pattern = re.compile('^(.*)\.([0-9]+)(\..*)$')
    ddl = [
        '''CREATE TABLE nodes (
            id integer primary key autoincrement,
            type varchar(10) not null,
            ns_id integer references ns(id),
            name varchar(255) not null,
            ext varchar(10))''',
        '''CREATE TABLE ns (
            id integer primary key autoincrement,
            fullname varchar(255) unique not null)''',
        '''CREATE TABLE revisions (
            id integer primary key autoincrement,
            node_id integer references nodes(id),
            time varchar(255) not null)''',
    ]

    def __init__(self, path):
        self.path = path
        self.version = None
        self.namespaces = [DokuNamespace("", parent=None, data=os.path.join(self.path, "data"))]

    def load(self):
        """Scans a directory tree and builds site structure"""
        root = self.namespaces[0]
        root.load()
        root.load_history()
        root.load_media()
        root.load_media_history()

    def summary(self):
        root = self.namespaces[0]
        root.summary()

    def persist(self, db):
        conn = sqlite3.connect(db)
        c = conn.cursor()

        # Create table
        [c.execute(s) for s in Doku.ddl]
        root = self.namespaces[0]
        root.persist(c)
        # Save (commit) the changes
        conn.commit()


        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        conn.close()


class DokuNamespace:
    sep = ":"

    def getPathFor(self, role="attic"):
        return os.path.join(self.data, role, self.getPath())

    def __init__(self, name, parent, data):
        self.data = data
        self.parent = parent
        self.name = name
        self.pages = {}
        self.medias = {}
        self.children = {}

        if self.parent:
            self.path = os.path.join(self.parent.getPath(), self.name)
            self.fullname = (self.parent.getFullName() + DokuNamespace.sep + self.name)
        else:
            self.path = self.name
            self.fullname = name
            #self.media_path = self.getPathFor("media")
            #self.attic_path = self.getPathFor("attic")

    def getPath(self):
        return self.path

    def getFullName(self):
        return self.fullname

    def load(self):
        """Scans a directory tree and builds site structure"""
        logging.debug("* Namespace: %s", self.getFullName())
        path = os.path.join(self.data, "pages", self.getPath())
        for name in os.listdir(path):
            entry = os.path.join(path, name)
            logging.debug("* Entry: %s", entry)
            if os.path.isdir(entry):
                ns = DokuNamespace(name, self, self.data)
                self.children[name] = ns
                ns.load()
            else:
                if not (name.endswith('.txt')):
                    logging.error("Page name not parsable: %s", name)
                    key = name
                key = name[:-4]
                self.pages[key] = DokuPage(self, key, os.path.getsize(entry))

                # self.load_media()

    def load_media(self):
        path = self.getPathFor("media")
        if not os.path.exists(path):
            return
        for name in os.listdir(path):
            entry = os.path.join(path, name)
            logging.debug("* Entry: %s", entry)
            if os.path.isdir(entry):
                if name in [self.children]:
                    ns = self.children['name']
                else:
                    ns = DokuNamespace(name, self, self.data)
                    self.children[name] = ns
                    ns.load_media()
            else:
                self.medias[name] = DokuMedia(self, name, os.path.getsize(entry))

    def load_history(self):
        path = self.getPathFor("attic")
        if not os.path.exists(path):
            return
        for name in os.listdir(path):
            if name == '_dummy':
                continue
            entry = os.path.join(path, name)
            logging.debug("* History: %s", entry)
            if os.path.isdir(entry):
                if name in [self.children]:
                    ns = self.children[name]
                else:
                    ns = DokuNamespace(name, self, self.data)
                    self.children[name] = ns
                    ns.load_history()
            else:
                self.add_version(name, self.pages, Doku.attic_pattern)


    def add_version(self, filename, collection, pattern=Doku.attic_pattern):
        m = pattern.match(filename)
        if m is not None:
            (name, date, ext) = m.groups()
            key = name + ext
            if key in collection:
                obj = collection[key]
            else:
                logging.warning("attic file %s:%s is orphan", self.getFullName(), filename)
                if collection is self.pages:
                    obj = DokuPage(self, key, -1, orphan=True)
                else:
                    obj = DokuMedia(self, key, -1, orphan=True)
                collection[key] = obj
            obj.add_version(date)
        else:
            logging.error("attic filename not parsable: '%s'", filename)


    def load_media_history(self):
        path = self.getPathFor("media_attic")
        if not os.path.exists(path):
            return
        for name in os.listdir(path):
            if name == '_dummy':
                continue
            entry = os.path.join(path, name)
            logging.debug("* Media history: %s", entry)
            if os.path.isdir(entry):
                if name in [self.children]:
                    ns = self.children[name]
                else:
                    ns = DokuNamespace(name, self, self.data)
                    self.children[name] = ns
                    ns.load_media_history()
            else:
                self.add_version(name, self.medias, Doku.media_attic_pattern)


    def summary(self):
        print("* Namespace: " + self.fullname)
        print("** pages: %d" % (len(self.pages)))
        for k, page in self.pages.items():
            page.summary()
        if len(self.medias):
            print("** medias: %d" % (len(self.medias)))
            for k, media in self.medias.items():
                media.summary()
        for k, ns in self.children.items():
            ns.summary()

    def persist(self, c):
        c.execute('''
        INSERT INTO ns (fullname) VALUES (?)
        ''', (self.fullname,))
        ns_id = c.lastrowid
        for k, page in self.pages.items():
            page.persist(c, ns_id)
            for k, media in self.medias.items():
                media.persist(c, ns_id)
        for k, ns in self.children.items():
            ns.persist(c)


class DokuNode:
    def __init__(self, ns, name, size, orphan=False):
        self.ns = ns
        self.name = name
        self.size = size
        self.orphan = orphan
        self.versions = []

    def add_version(self, date):
        self.versions.append(date)

    def summary(self):
        print("  - [%s] %s - %d bytes - %d revisions : %s" % (
            self.__class__.__name__, self.name, self.size, self.getRevCount(), self.getStatus()))

    def getRevCount(self):
        return len(self.versions)

    def getStatus(self):
        if self.orphan:
            return "orphan"
        else:
            return "ok"

    def persist(self, c, ns_id):
        c.execute('''
        INSERT INTO nodes (type, ns_id, name) VALUES (?, ?, ?)
        ''', (self.__class__.__name__, ns_id, self.name))
        node_id = c.lastrowid
        for rev in self.versions:
            c.execute('''
            INSERT INTO revisions (node_id, time) VALUES (?, ?)
            ''', (node_id, rev))


class DokuPage(DokuNode):
    def __init__(self, ns, name, size, orphan=False):
        DokuNode.__init__(self, ns, name, size, orphan)
        logging.debug("Page: %s:%s", ns.name, name)


class DokuMedia(DokuNode):
    def __init__(self, ns, name, size, orphan=False):
        DokuNode.__init__(self, ns, name, size, orphan)
        logging.debug("Media: %s:%s", ns.name, name)

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
