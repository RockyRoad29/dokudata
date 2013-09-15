import logging
from doku import Doku

__author__ = 'mich'

if __name__ == "__main__":

    wikiset = [
        [
        's2m-130911',
        '/home/mich/services/sel2mers/mirror/sel2mers/wiki'
        ],[
        's2m-130913',
        '/home/mich/services/sel2mers/mirror/sel2mers/doku'
        ]]

    logging.basicConfig(level=logging.INFO)

    for (name, path) in wikiset:
        print("#+TITLE", name, path)
        wiki = Doku(path)
        wiki.load()
        wiki.summary()
