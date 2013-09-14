import os
from doku import Doku

__author__ = 'mich'

if __name__ == "__main__":
#logging.basicConfig(level=logging.DEBUG)

#    wiki = Doku('/home/mich/services/sel2mers/mirror/sel2mers/doku')
    wiki = Doku('/home/mich/services/sel2mers/mirror/sel2mers/wiki')
    #    wiki = Doku('/usr/local/www/sel2mers-doku')
    wiki.load()

    #print(repr(wiki))
    # import pprint, inspect
    #pprint.pprint(inspect.getmembers(wiki))

    wiki.summary()

    db = '/tmp/doku.db'
    if os.path.exists(db):
        os.unlink(db)
    wiki.persist(db)