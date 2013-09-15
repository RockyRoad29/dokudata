import logging
from doku import Doku


__author__ = 'mich'

if __name__ == "__main__":
    if True:
        WIKINAME = 's2m-130911'
        WIKIPATH = '/home/mich/services/sel2mers/mirror/sel2mers/wiki'
    else:
        WIKINAME = 's2m-130913'
        WIKIPATH = '/home/mich/services/sel2mers/mirror/sel2mers/doku'

    basename = "/tmp/doku-" + WIKINAME
    logging.basicConfig(level=logging.INFO, filename=basename + ".log", filemode="w")
    wiki = Doku(WIKIPATH)

    wiki.load()
    wiki.persist2db(basename + ".db",overwrite=True)