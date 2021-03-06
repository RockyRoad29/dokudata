import logging
from doku import Doku

__author__ = 'mich'

if __name__ == "__main__":

    wikiset = [
        [
        # 's2m-130911',
        # '/home/mich/services/sel2mers/mirror/sel2mers/wiki'
        # ],[
        # 's2m-130913',
        # '/home/mich/services/sel2mers/mirror/sel2mers/doku'
        # ],[
        's2m-sink',
        '/home/mich/services/sel2mers/wiki-maint'
        ]]

    logging.basicConfig(level=logging.DEBUG)

    for (name, path) in wikiset:
        print("#+TITLE", name, path)
        wiki = Doku(path)
        wiki.load()
        wiki.summary()
