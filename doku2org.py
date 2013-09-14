import logging
import os
from doku import Doku

__author__ = 'mich'

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

#    wiki = Doku('/home/mich/services/sel2mers/mirror/sel2mers/doku')
    wiki = Doku('/home/mich/services/sel2mers/mirror/sel2mers/wiki')
#    wiki = Doku('/usr/local/www/sel2mers-doku')

    wiki.load()

    wiki.summary()
