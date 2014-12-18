# README

* version: 1.2
* date: Dec 13, 2014

## Program Requirements
### Required
* [Python 2.7](https://www.python.org/downloads/)
	* This script is written and tested in Python 2.7 and Windows 7/8
* [uTorrent 3.0+](http://www.utorrent.com/downloads/complete/os/win/track/stable)
* [Java Runtime Environment 32-bit](https://java.com/en/download/manual.jsp)
### Optional
* [Pushbullet](https://www.pushbullet.com/)
	* pushbullet is a free application that allows you to send notifications, lists, files, etc. 
	across multiple devices including iOS, android, windows(desktop), chrome, firefox

## How do I get set up?

### Set up uTorrent
#### How to set up access to uTorrent for the script
* Go to `preferences>advanced>Web UI`
* Check the box `Enable Web UI`
* Fill in a username and password
* Optionally create an alternative listening port
#### How to run script on each torrent
* Go to `preferences>advanced>run program>run program when torrent changes state`
	* input(with quotes): `"path\to\pythonw.exe" "path\to\autohtpc.py" %I %P %S`
* it is recommended to at least keep seeding for a few minutes to allow time for 
  the script to finish extracting and moving files before removing the torrent
  from uTorrent, if enabled
* Go to `preferences>queueing>minimum seeding time(minutes)`
	* recommended to set to at least 10 minutes to allow time for 
	the script to finish extracting and moving files

### Set up autoHTPC
* edit included config.cfg file

General      | 
------------:| :------------
path         | location for files to be extracted/copied to before processing by FileBot
overwrite    | (True/False) overwrite files that are already present in final directory
remove       | (True/False) remove torrent from uTorrent when done seeding
notify       | (True/False) send a notification when done processing a torrent
notifyRemove | (True/False) send a notification when removing a torrent
pause        | (True/False) pause the script at the end before closing

Client       | 
------------:| :------------
port         | Either the alternative listening port in Web UI settings or the connection port
username     | Web UI username
password     | Web UI password

Email        | 
------------:| :------------
enable       | (True/False) Use email notifications
SMTPServer   | Email server (gmail is default)
SMTPPort     | Email port (gmail is default)
username     | Your email username (example@gmail.com)
password     | Your email password
emailTo      | What addresses to email notification to, separated by (pipe character)

PushBullet   | 
------------:| :------------
enable       | (True/False) Use PushBullet for notifications
token        | Your [access token](https://www.pushbullet.com/account) from Pushbullet
devices      | Can either be a list of specific device names, separated by (pipe character), or leave blank for all devices

Extensions   | 
------------:| :------------
video        | You can either leave it as-is or modify the list, separating each extension by (pipe character)
subtitle     | You can either leave it as-is or modify the list, separating each extension by (pipe character)
readme       | You can either leave it as-is or modify the list, separating each extension by (pipe character)
archive      | You can either leave it as-is or modify the list, separating each extension by (pipe character)
ignore       | Any file with any of the words in this list will be ignored, even with a desired extension, separated by (pipe character)

* set up labels in the labels folder (the script will ignore any torrent without a label and accompanying config file)

Type         | 
------------:| :------------
video        | (True/False) For this label, do you want to keep files of this type?
subtitle     | (True/False) For this label, do you want to keep files of this type?
readme       | (True/False) For this label, do you want to keep files of this type?

Filebot      | 
------------:| :------------
database     | TV: `TVRage, AniDB, TheTVDB` Movies: `OpenSubtitles, IMDb, TheMovieDB`
format       | How you want your file names to be [formatted](http://www.filebot.net/naming.html)
language     | The [2-letter language code](http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) for episode/movie titles 
path         | The final path for your file(s)