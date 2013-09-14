import logging
import os
import re
from dokunode import DokuPage, DokuMedia

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
                self.add_version(name, self.pages, DokuNamespace.attic_pattern)


    def add_version(self, filename, collection, pattern=attic_pattern):
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
                self.add_version(name, self.medias, DokuNamespace.media_attic_pattern)


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
