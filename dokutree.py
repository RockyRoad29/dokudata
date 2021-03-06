import logging
import os
import re

__author__ = 'mich'


class DokuTree:
    """Abstract Base Class. Manages one of the dokuwiki data subdirectories : pages, meta, media, attic etc ...

    They are all organized into namespaces, which they walk through to collect various files associated to
    nodes (':py:class:`DokuNode`) .
    """
    #: filename pattern
    pattern = re.compile('^(.*)(\.[^.]*)$')


    def __init__(self, root, treename):
        self.root = root
        self.treename = treename
        logging.info("* Loading " + treename)

    def getPattern(self):
        return self.pattern

    def parse(self, filename):
        m = self.getPattern().match(filename)
        if not m:
            raise ValueError("Parsing %s as %s entry with /%s/", filename, self.treename, self.getPattern().pattern )
        return tuple(m.groups())

    def add_node(self, entry, abspath, ns):
        raise NotImplementedError("Pure Virtual")

    def loadRoot(self):
        return self.load(self.root, self.root.getPathFor(self.treename))

    def load(self, ns, dirpath):
        """Scans a directory tree and builds site structure"""
        assert(dirpath)
        logging.info("* Loading tree: %s", dirpath)
        #dirpath = ns.getPath(self.treename)
        for entry in os.listdir(dirpath):
            if self.ignore(entry):
                continue
            abspath = os.path.join(dirpath, entry)
            logging.debug("* direntry: %s", abspath)
            if os.path.isdir(abspath):
                self.load(ns.getNamespace(entry), abspath)
            else:
                self.add_node(entry, abspath, ns)

    def ignore(self, entry):
        return (entry=='_dummy')

    def getsize(self, abspath):
        return os.path.getsize(abspath)


class DokuPagesTree(DokuTree):
    """
    >>> tree = DokuPagesTree(None)
    >>> tree.parse("calendrier.txt")
    ('calendrier', '.txt')

    """
    pattern = re.compile('^(.*)(\.txt)$')
    def __init__(self, doku):
        super().__init__(doku, "pages")

    def _parse0(self, entry):
        if not (entry.endswith('.txt')):
            logging.error("Page name not parsable: %s", entry)
            name = entry
            return (name, None)
        else:
            name = entry[:-4]
            return (name, '.txt')



    def add_node(self, entry, abspath, ns):
        (name, ext) = self.parse(entry)
        if ext != '.txt':
            logging.error("Page extension should be .txt", entry)
            name = entry
        ns.addPage(name, self.getsize(abspath))


class DokuMediaTree(DokuTree):
    """
    >>> tree = DokuMediaTree(None)
    >>> tree.parse("calendrier.jpg")
    ('calendrier', '.jpg')

    """
    def __init__(self, doku):
        super().__init__(doku, "media")

    # def parse(self, filename):
    #     return (filename)

    def add_node(self, entry, abspath, ns):
        # here, we parse just for checking
        (name, ext) = self.parse(entry)
        # ns.addMedia(name+ext, self.getsize(abspath))
        # we'd better keep full name here
        ns.addMedia(entry, self.getsize(abspath))

class DokuAttic(DokuTree):
    """
        .. rubric:: Testing filenames pattern

    :py:attr:`pattern` - filename pattern.

    >>> tree = DokuAttic(None)
    >>> tree.parse("calendrier.1367320658.txt.gz")
    ('calendrier', '1367320658', '.txt.gz')
"""
    pattern = re.compile('^(.*)\.([0-9]+)(\..*)$')

    def __init__(self, doku, treename="attic"):
        super().__init__(doku, treename)

    def add_node(self, entry, abspath, ns):
        (name, rev, ext) = self.parse(entry)
        page = ns.getPage(name)
        page.addRevision(rev, self.getsize(abspath))

class DokuMediaAttic(DokuAttic):
    """
        .. rubric:: Testing filenames pattern

    :py:attr:pattern - Media attic filename pattern

    >>> tree = DokuMediaAttic(None)
    >>> tree.parse("fiche_inscription_v1.1336687823.pdf")
    ('fiche_inscription_v1', '1336687823', '.pdf')
    """

    def __init__(self, doku):
        super().__init__(doku, "media_attic")

    def add_node(self, entry, abspath, ns):
        (name, rev, ext) = self.parse(entry)
        media = ns.getMedia(name+ext)
        media.addRevision(rev, self.getsize(abspath))

class DokuMetaTree(DokuTree):

    def __init__(self, doku):
        super().__init__(doku, "meta")

    def ignore(self, entry):
        return super().ignore(entry) or (entry.endswith('.trimmed')) or (entry == '_htcookiesalt')

    def add_node(self, entry, abspath, ns):
        (name, ext) = self.parse(entry)
        page = ns.getPage(name)
        size = self.getsize(abspath)
        with open(abspath) as f:
            contents = f.read()
        if ext=='.changes':
            page.setChanges(contents)
        elif (ext == '.indexed'):
            page.setIndexed(contents)
        elif (ext == '.meta'):
            page.setMeta(contents)
        else:
            logging.warning("Unexpected meta entry : %s", entry)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)

