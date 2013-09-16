import logging
from doku import Doku


__author__ = 'mich'

def _doku2db(name, path):
    pass


def doku2db(name, path):
    global basename, wiki
    basename = "/tmp/doku-" + name
    logging.basicConfig(level=logging.INFO, filename=basename + ".log", filemode="w")
    wiki = Doku(path)
    wiki.load()
    wiki.persist2db(basename + ".db", overwrite=True)


if __name__ == "__main__":
    # doku2db('s2m-130911',
    #         '/home/mich/services/sel2mers/mirror/sel2mers/wiki')
    # doku2db('s2m-130913',
    #         '/home/mich/services/sel2mers/mirror/sel2mers/doku')
    #
    doku2db('s2m-sink',
            '/home/mich/services/sel2mers/wiki-maint')
