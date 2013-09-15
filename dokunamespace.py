import logging
import os
import re
from dokunode import DokuPage, DokuMedia, DokuFile


__author__ = 'mich'


class DokuNamespace:
    """
        .. rubric:: Testing filenames patterns

    :py:attr:`attic_pattern` - Page attic filename pattern.

    >>> m = DokuNamespace.attic_pattern.match("calendrier.1367320658.txt.gz")
    >>> [m.group(i) for i in (1, 2, 3)]
    ['calendrier', '1367320658', '']

    :py:attr:media_attic_pattern - Media attic filename pattern

    >>> m = DokuNamespace.media_attic_pattern.match("fiche_inscription_v1.1336687823.pdf")
    >>> [m.group(i) for i in (1, 2, 3)]
    ['fiche_inscription_v1', '1336687823', '.pdf']
    """

    #: Page attic filename pattern.
    attic_pattern = re.compile('^(.*)\.([0-9]+)()\.txt\.gz')
    #: Media attic filename pattern
    media_attic_pattern = re.compile('^(.*)\.([0-9]+)(\..*)$')

    #: Namespace separator
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
            self.fullname = (self.parent.getFullName() + self.name + DokuNamespace.sep)
        else:
            self.path = self.name
            self.fullname = DokuNamespace.sep
            #self.media_path = self.getPathFor("media")
            #self.attic_path = self.getPathFor("attic")

    def getPath(self):
        return self.path

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
        if name in [self.children]:
            ns = self.children[name]
        else:
            ns = DokuNamespace(name, self, self.data)
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

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
