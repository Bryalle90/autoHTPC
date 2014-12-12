# README #

version: 1.1
date: Dec 12, 2014

## Program Requirements ##

### Required ###

* Python 2.7
* uTorrent 3.0+

## How do I get set up? ##

* In uTorrent go to settings , advanced , run program , run program when torrent changes state
* input(with quotes):
                "path\to\pythonw.exe" "path\to\autohtpc.py" %I %P %S
* edit included config.cfg file
* set up labels in the labels folder 
the script will ignore any torrent without a label and accompanying config file
* it is recommended to at least keep seeding for a few minutes to allow time for 
  script to finish extracting and moving files before removing the torrent
  from uTorrent, if enabled

## FileBot ##

* you must set up label configs in order to use filebot to rename files