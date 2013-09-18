dokudata
========

Dokuwiki cms maintenance helpers in python

### Welcome
Dokudata is a python project designed to help webmaster to check and maintain their dokuwiki directory tree.

This is not a plugin. You can use it on your localhost wiki or you need to have ssh access to your server to run scripts.

### Loading and checking your data directory
Dokudata scans your data directory tree to build its own representation of your wiki contents, reporting missing files.

### Usage
 `doku2org` script uses dokudata engine to build a report in emacs org-mode format.

`doku2db` script creates an sqlite database of your pages and media. 
 You may then use it to retrieve duplicate or lost entries, do stats ... whatever you need. 
