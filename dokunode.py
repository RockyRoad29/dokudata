import logging
from phpserialize import serialize, unserialize

__author__ = 'mich'


class DokuFile(object):
    """
    Represents a data/**/*.* file.
    """
    #: special negative size value to mark a missing file
    MISSING = -1

    def __init__(self, size):
        self.size = size

    def isMissing(self):
        return self.size < 0


class DokuNodeFile(DokuFile):
    """
    Represents a data/**/*.*  file which
    is associated to a `DokuNode` (`DokuPage` or `DokuMedia`)
    and is further characterized by a timestamp (:py:attr:`date`).
    """

    def __init__(self, node, size):
        super().__init__(size)
        self.node = node

class DokuRevision(DokuNodeFile):
    """
    Represents a data/*attic/**/*.*  file.
    It is associated to a `DokuNode` (`DokuPage` or `DokuMedia`)
    and is further characterized by a timestamp (:py:attr:`date`).
    """

    def __init__(self, node, date, size):
        super().__init__(node, size)
        self.date = date
        self.meta = None

    def persist2db(self, c, node_id):
        c.execute('''
        INSERT INTO revisions (node_id, time, size, meta) VALUES (?, ?, ?, ?)
        ''', (node_id, self.date, self.size, serialize(self.meta)))

    def setMetaFields(self, dict):
        self.meta = dict
        logging.debug("  Revision fields: %s", repr(self.meta))

class DokuIndexed(DokuNodeFile):
    """
    Represents a data/meta/**/*.indexed  file.
    """
    pass


class DokuChanges(DokuNodeFile):
    """
    Represents a data/meta/**/*.changes  file.
    """
    pass


class DokuMeta(DokuNodeFile):
    """
    Represents a data/meta/**/*.meta  file.
    """
    pass

class DokuNode(DokuFile):
    """
    This is a base class for dokuwiki browsable objects, a page or media object.
    Element of a given `DokuNamespace`, it carries history, meta and indexing information.
    """
    def __init__(self, ns, name, size):
        super().__init__(size)
        self.ns = ns
        self.name = name
        self.revisions = {}
        self.sz_changes = None
        self.sz_meta = None
        self.sz_indexed = None
        self.meta = None

    def isMissing(self):
        return self.size < 0

    def addRevision(self, date, size):
        assert(date not in self.revisions)
        rev = DokuRevision(self, date, size)
        self.revisions[date] = rev
        return rev

    def getRevision(self, date):
        if not date in self.revisions:
            logging.warning("Revision %s not found for %s", date, self.getFullname())
            rev = self.addRevision(date, DokuFile.MISSING)
        else:
            rev = self.revisions[date]
        return rev

    def setChanges(self, text):
        assert self.sz_changes is None
        self.sz_changes = DokuChanges(self, len(text))
        for line in text.splitlines():
            fields = line.split("\t")
            date = fields[0]
            z = zip(('ip', 'mode', 'name', 'user', 'summary', 'extra', 'flags'), fields[1:])
            rev = self.getRevision(date)
            rev.setMetaFields(dict(z))

    def setIndexed(self, text):
        assert self.sz_indexed is None
        self.sz_indexed = DokuIndexed(self, len(text))

    def setMeta(self, text):
        assert self.sz_meta is None
        self.sz_meta = DokuMeta(self, len(text))
        try:
            self.meta = unserialize(text.encode(), decode_strings=True)
            logging.info(repr(self.meta))
        except Exception as e:
            logging.error(e)
            logging.info(text)
            self.meta = text
            raise e

    def summary(self):
        print("  - [%s] %s - %d bytes - %d revisions : %s" % (
            self.__class__.__name__, self.name, self.size, self.getRevCount(), 'MISSING' if self.isMissing() else ''))

    def getRevCount(self):
        return len(self.revisions)

    def persist2db(self, c, ns_id):
        sz_changes = self.sz_changes.size if self.sz_changes else self.MISSING
        sz_indexed = self.sz_indexed.size if self.sz_indexed else self.MISSING
        sz_meta = self.sz_meta.size if self.sz_meta else self.MISSING
        c.execute('''
        INSERT INTO nodes (type, ns_id, name, size,
                           sz_changes, sz_indexed, sz_meta, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.__class__.__name__, ns_id, self.name, self.size,
            sz_changes, sz_indexed, sz_meta, serialize(self.meta)
        ))
        node_id = c.lastrowid
        for date, rev in self.revisions.items():
            rev.persist2db(c, node_id)

    def getFullname(self):
        return self.ns.getFullName() + self.ns.sep + self.name


class DokuPage(DokuNode):
    def __init__(self, ns, name, size):
        DokuNode.__init__(self, ns, name, size)
        logging.debug("Page: %s:%s", ns.name, name)


class DokuMedia(DokuNode):
    def __init__(self, ns, name, size):
        DokuNode.__init__(self, ns, name, size)
        logging.debug("Media: %s:%s", ns.name, name)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
