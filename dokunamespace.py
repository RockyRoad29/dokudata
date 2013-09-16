import logging
import os
import re
from dokunode import DokuPage, DokuMedia, DokuFile


__author__ = 'mich'


class DokuNamespace:
    """
    """
    #: Namespace separator
    sep = ":"

    def getDataPath(self):
        return self.parent.getDataPath()

    def getPathFor(self, tree="attic"):
        return os.path.join(self.getDataPath(), tree, self.getPath())

    def __init__(self, name, parent):
        assert(name and parent)
        self.parent = parent
        self.name = name
        self.pages = {}
        self.medias = {}
        self.children = {}
        self.fullname = (self.parent.getFullName() + self.name + DokuNamespace.sep)

    def getPath(self):
        return os.path.join(self.parent.getPath(),self.name)

    def getFullName(self):
        return self.fullname

    def addPage(self, name, size):
        assert(name not in self.pages)
        page = DokuPage(self, name, size)
        self.pages[name] = page
        return page

    def getPage(self, name):
        if not name in self.pages:
            logging.warning("Page %s not found in %s", name, self.fullname)
            page = self.addPage(name, DokuFile.MISSING)
        else:
            page = self.pages[name]
        return page

    def addMedia(self, name, size):
        assert(name not in self.medias)
        media = DokuMedia(self, name, size)
        self.medias[name] = media
        return media

    def getMedia(self, name):
        if not name in self.medias:
            logging.warning("Media %s not found in %s", name, self.fullname)
            media = self.addMedia(name, -1)
        else:
            media = self.medias[name]
        return media

    def getNamespace(self, name):
        if name in self.children:
            ns = self.children[name]
        else:
            ns = DokuNamespace(name, self)
            self.children[name] = ns
        return ns


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

    def persist2db(self, c):
        c.execute('''
        INSERT INTO ns (fullname) VALUES (?)
        ''', (self.fullname,))
        ns_id = c.lastrowid
        for k, page in self.pages.items():
            page.persist2db(c, ns_id)
        for k, media in self.medias.items():
            media.persist2db(c, ns_id)
        for k, ns in self.children.items():
            ns.persist2db(c)

    def getDoku(self):
        return self.parent.getDoku()

class DokuRoot(DokuNamespace):

    def __init__(self, wiki):
        self.doku = wiki
        self.data = os.path.join(wiki.path, "data")
        self.name = ""
        self.fullname = DokuNamespace.sep
        self.pages = {}
        self.medias = {}
        self.children = {}

    def getDataPath(self):
        return self.data

    def getDoku(self):
        return self.doku

    def getPath(self):
        return ''


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
