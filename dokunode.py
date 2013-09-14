import logging

__author__ = 'mich'


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

    def persist2db(self, c, ns_id):
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
