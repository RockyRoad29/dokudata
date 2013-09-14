import logging
import os
import re
from dokunode import DokuPage, DokuMedia

__author__ = 'mich'


class DokuTree:
    """Abstract Base Class. Manages one of the dokuwiki data subdirectories : pages, meta, media, attic etc ...

    They are all organized into namespaces, which they walk through to collect various files associated to
    nodes (':py:class:`DokuNode`) .
    """
    #: filename pattern
    pattern = re.compile('^(.*)\.([0-9]+)(\..*)$')

    def __init__(self, doku, treename):
        self.doku = doku
        self.treename = treename
        logging.info("* Loading " + treename)

    def getPattern(self):
        return DokuTree.pattern;

    def parse(self, filename):
        m = self.getPattern().match(filename)
        if not m:
            raise ValueError("Parsing %s as %s entry", filename, self.treename )
        return [m.groups()]

    def add_node(self, entry, size, ns):
        raise NotImplementedError("Pure Virtual")

    def load(self, dirpath, ns):
        """Scans a directory tree and builds site structure"""
        if dirpath is None:
            dirpath = os.path.join(self.doku.data, self.treename)
        #dirpath = ns.getPath(self.treename)
        for entry in os.listdir(dirpath):
            if entry=='_dummy':
                continue
            abspath = os.path.join(dirpath, entry)
            logging.debug("* direntry: %s", abspath)
            if os.path.isdir(abspath):
                self.load(abspath, ns.getNamespace(entry))
            else:
                self.add_node(entry, os.path.getsize(abspath), ns)

class DokuPages(DokuTree):
    def __init__(self, doku):
        super().__init__(doku, "pages")

    def parse(self, entry):
        if not (entry.endswith('.txt')):
            logging.error("Page name not parsable: %s", entry)
            name = entry
        else:
            name = entry[:-4]
        return (name,None, None)

    def add_node(self, entry, size, ns):
        name = self.parse(entry)[0]
        ns.addPage(name, size)

class DokuMedia(DokuTree):
    def __init__(self, doku):
        super().__init__(doku, "media")

    def parse(self, filename):
        return (filename)

    def add_node(self, entry, size, ns):
        (name) = self.parse(entry)
        ns.addMedia(name, size)

class DokuAttic(DokuTree):
    """
        .. rubric:: Testing filenames pattern

    :py:attr:`pattern` - filename pattern.

    >>> tree = DokuAttic(None)
    >>> tree.parse("calendrier.1367320658.txt.gz")
    ['calendrier', '1367320658', 'txt.gz']
"""
    def __init__(self, doku):
        super().__init__(doku, "attic")

    def add_node(self, entry, size, ns):
        (name, rev, ext) = self.parse(entry)
        page = ns.getPage(name)
        page.add_version(rev, size)

class DokuMediaAttic(DokuTree):
    """
        .. rubric:: Testing filenames pattern

    :py:attr:pattern - Media attic filename pattern

    >>> tree = DokuMediaAttic(None, "media_attic")
    >>> tree.parse("fiche_inscription_v1.1336687823.pdf")
    ['fiche_inscription_v1', '1336687823', '.pdf']
    """

    def __init__(self, doku):
        super().__init__(doku, "pages")

    def add_node(self, entry, size, ns):
        (name, rev, ext) = self.parse(entry)
        media = ns.getMedia(name + ext)
        media.add_version(rev, size)



if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)

