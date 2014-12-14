import os
import sys
import time
import errno
import shutil
import binascii
import subprocess
import ConfigParser
import libs.client.utorrent as torrent_client

from libs.unrar2 import RarFile
from libs.notifications.pushbullet import PushBullet
from libs.notifications.email import Email

NAME = 'Bryan Allen'
VERSION = '1.2'

class Process():		
	def getStateType(self, state):
		state = int(state)
		if state == 4 or state == 5 or state == 7 or state == 8 or state == 10:
			return 'seeding'
		elif state == 6 or state == 9:
			return 'downloading'
		elif state == 20:
			return 'moving'
		elif state == 11:
			return 'finished'
		elif state == 3:
			return 'paused'
		return None
		
	def readConfig(self, path, fname):
		file = os.path.normpath(os.path.join(path, fname) + '.cfg')
		config = ConfigParser.ConfigParser()
		config.read(file)
		return config
			
	def connect(self, port, user, pw):
		self.uTorrent = torrent_client.TorrentClient()
		url = 'http://localhost:' + port + '/gui/'
		
		if not self.uTorrent.connect(url, user, pw):
			print 'could not connect to utorrent - exiting' + '\n'
			sys.exit(-1)
			
	def getTorrentInfo(self, hash):
		torrent = self.uTorrent.find_torrent(hash)
		info = self.uTorrent.get_info(torrent)
		return info
		
	def getExtensions(self, keep_ext, extensions):
		ext_list = []
		if keep_ext['video']:
			ext_list.extend(extensions['video'])
		if keep_ext['subs']:
			ext_list.extend(extensions['subs'])
		if keep_ext['readme']:
			ext_list.extend(extensions['readme'])
		return tuple(ext_list)
		
	def isSubstring(self, list, searchstring):
		for item in list:
			if item in searchstring:
				return True
		return False

	def isMainRar(self, f):
		with open(f, "rb") as this_file:
			byte = this_file.read(12)

		spanned = binascii.hexlify(byte[10])
		main = binascii.hexlify(byte[11])

		if spanned == "01" and main == "01":	# main rar archive in a set of archives
			return True
		elif spanned == "00" and main == "00":	# single rar
			return True
		return False
		
	def filterFiles(self, files, extensions, ignore):
		keep = []
		for file in files:
			if file.endswith(extensions):
				if not (self.isSubstring(ignore, os.path.split(file)[1])):
					keep.append(file)
		return keep
		
	def filterArchives(self, files, extensions, ignore):
		keep = []
		for file in files:
			if file.endswith(extensions):
				if not (self.isSubstring(ignore, os.path.split(file)[1])):
					if file.endswith('.rar'):
						if self.isMainRar(file):
							keep.append(file)
					else:
						keep.append(file)
		return keep
		
	def extract(self, file, destination):
		file_name = os.path.split(file)[1]
		print 'attempting to extract:', file_name
		try:
			rar_handle = RarFile(file)
			for rar_file in rar_handle.infolist():
				sub_path = os.path.join(destination, rar_file.filename)
				if rar_file.isdir and not os.path.exists(sub_path):
					os.makedirs(sub_path)
				else:
					rar_handle.extract(condition=[rar_file.index], path=destination, withSubpath=True, overwrite=False)
			del rar_handle
			print '\tSuccess!'
		except Exception, e:
			print '\tFailed:', str(e)
			
	def createDir(self, directory):
		if not os.path.isdir(directory):
			try:
				os.makedirs(directory)
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise
				pass
				
	def copyFile(self, source_file, destination):
		if os.path.isfile(source_file):
			file_name = os.path.split(source_file)[1]
			destination_file = os.path.join(destination, file_name)
			print 'attempting to copy:', file_name
			if not os.path.isfile(destination_file):
				try:
					shutil.copy2(source_file, destination_file)
					print '\tSuccess!'
				except Exception, e:
					print '\tFailed:',str(e)
			else:
				print '\t', file_name, 'already exists in destination - skipping'
				
	def cleanDir(self, path, desiredExtensions, ignore):
		# remove any file that doesn't have a desired extension or has an ignore word in the file name
		for dirName, subdirList, fileList in os.walk(path):
			for file in fileList:
				if not file.endswith(desiredExtensions) or self.isSubstring(ignore, file):
					try:
						print 'removing file:', file
						os.remove(os.path.normpath(os.path.join(dirName, file)))
					except Exception, e:
						print 'could not delete ' + file + ': ' + str(e)
						
		# remove any folder that is completely empty
		for dirName, subdirList, fileList in os.walk(path, topdown=False):
			if len(fileList) == 0 and len(subdirList) == 0:
				print 'removing directory:', dirName
				os.rmdir(dirName)
			
	def renameAndMove(self, filebot, source, dest, db, format):
		fb_args = [
			filebot,
			'-rename', source,
			'--output', dest,
			'--db', db,
			'--format', format,
			'-non-strict'
		]
		try:
			subprocess.call(fb_args)
		except Exception, e:
			print 'could not rename file:', str(e)
	
	def removeTorrent(self, hash):
		torrent = self.uTorrent.find_torrent(hash)
		self.uTorrent.delete_torrent(torrent)
		
	def sendPush(self, token, devices, notification):
		pb = PushBullet(token)
		subject = notification['subject']
		body = 'title: ' + notification['title'] + '\n' +\
				'label: ' + notification['label'] + '\n' +\
				'date: ' + notification['date'] + '\n' +\
				'time: ' + notification['time'] + '\n' +\
				'action: ' + notification['action']
		
		if not devices == ['']:
			ds = pb.getDevices()
			for d in ds:
				if d['pushable'] and d['nickname'] in devices:
					pb.pushNote(d['iden'], subject, body)
		else:
			pb.pushNote('', subject, body)
	
	def sendEmail(self, email_info, notification):
		em = Email()
		
		header = 'Content-type: text/html\n' + 'Subject:' + notification['subject'] + '\n'
		body = """
		<html xmlns="http://www.w3.org/1999/xhtml">
			<head>
				<style type="text/css">
				table.gridtable {
					font-family: verdana,arial,sans-serif;
					font-size:11px;
					color:#333333;
					border-width: 0px;
					border-color: green;
					border-collapse: collapse;
				}
				table.gridtable th {
					border-width: 0x;
					padding: 8px;
					border-style: solid;
					border-color: green;
					background-color: green;
					align: left;
				}
				table.gridtable td {
					border-width: 0px;
					padding: 8px;
					border-style: solid;
					border-color: white;
					background-color: #ffffff;
				}
				</style>
			</head>
			<body bgcolor="black">
				<table class="gridtable">
					<colgroup>
						<col/>
						<col/>
					</colgroup>
					<tr><td>Title:</td><td>%s</td></tr>
					<tr><td>Label:</td><td>%s</td></tr>
					<tr><td>Date:</td><td>%s</td></tr>
					<tr><td>Time:</td><td>%s</td></tr>
					<tr><td>Action:</td><td>%s</td></tr>
				</table>
			</body>
		</html>
		""" % (notification['title'], notification['label'], notification['date'], notification['time'], notification['action'])
		msg = header + body
		
		em.send_email(email_info, msg)
		
if __name__ == "__main__":
	if len(sys.argv) == 4:
		print 'autoHTPC'
		print 'by:', NAME
		print 'version:', VERSION
		print ''
		
		root = os.path.dirname(os.path.realpath(sys.argv[0]))
		config_folder = os.path.normpath(os.path.join(root, 'cfg'))
		labels_folder = os.path.normpath(os.path.join(config_folder, 'labels'))
		filebot = os.path.normpath(os.path.join(root, 'libs', 'FileBot_4.5', 'filebot'))
		
		# create torrent processor
		processor = Process()
		
		# get torrent info from uTorrent
		torrent_hash = sys.argv[1]							 # Hash of the torrent, %I
		torrent_prev = processor.getStateType(sys.argv[2])	 # Previous state of the torrent, %P
		torrent_state = processor.getStateType(sys.argv[3])	 # Current state of the torrent, %S
		
		print 'info received:'
		print '--'
		print 'torrent hash:    ' + torrent_hash
		print 'torrent state:   ' + torrent_state
		print 'previous state:  ' + torrent_prev
		print '--\n'
		
		# open the main config
		try:
			config = processor.readConfig(config_folder, 'config')
			print 'config file read\n'
		except Exception, e:
			print 'could not open config:', str(e)
			sys.exit(0)
		
		# connect to uTorrent
		port = str(config.get("Client", "port"))
		user = config.get("Client", "username")
		pw = config.get("Client", "password")
		processor.connect(port, user, pw)
		print 'connected to uTorrent\n'
		
		# get info for torrent
		print 'Getting torrent info from uTorrent'
		print '--'
		torrent = processor.getTorrentInfo(torrent_hash)
		print 'torrent name:    ' + torrent['name']
		print 'torrent label:   ' + torrent['label']
		print '--\n'
		
		# process torrent files
		if torrent['label'] == '':
			print 'label is blank - skipping'
		elif os.path.isfile(os.path.join(labels_folder, torrent['label']) + '.cfg'):
			action = None
			# if torrent goes from downloading -> seeding, copy and extract files
			if (torrent_prev == 'downloading') and (torrent_state == 'seeding' or torrent_state == 'moving'):
				# get what extensions we want
				extensions = {
					'video': config.get("Extensions","video").split('|'),
					'subs': config.get("Extensions","subtitle").split('|'),
					'readme': config.get("Extensions","readme").split('|'),
				}
				label_config = processor.readConfig(labels_folder, torrent['label'])
				keep_ext = {
					'video': label_config.getboolean("Type", "video"),
					'subs': label_config.getboolean("Type", "subtitle"),
					'readme': label_config.getboolean("Type", "readme")
				}
				desiredExtensions = processor.getExtensions(keep_ext, extensions)
				print 'looking for files with these extensions:', desiredExtensions, '\n'
				
				
				# get words we don't want
				wordsToIgnore = config.get("Extensions","ignore").split('|')
				print 'ignoring files with these words in the file name:', wordsToIgnore, '\n'
				
				# get what files to keep from torrent folder
				filesToCopy = processor.filterFiles(torrent['files'], desiredExtensions, wordsToIgnore)
				
				# get archives to extract from
				archiveExtensions = tuple(config.get("Extensions","archive").split('|'))
				filesToExtract = processor.filterArchives(torrent['files'], archiveExtensions, wordsToIgnore)
				
				# copy/extract files to processing directory
				processingDir = os.path.normpath(os.path.join(config.get("General","path"), torrent['name']))
				processor.createDir(processingDir)
				print 'copying and extracting files to:\n\t', processingDir
				print '--'
				for file in filesToCopy:
					processor.copyFile(file, processingDir)
				for file in filesToExtract:
					processor.extract(file, processingDir)
				print '--\n'
				
				# clean out unwanted files from processing dir
				print 'cleaning unwanted files in:\n\t', processingDir
				print '--'
				processor.cleanDir(processingDir, desiredExtensions, wordsToIgnore)
				print '--\n'
				
				# use filebot to rename files and move to final directory
				print 'sending file info to filebot\n'
				outputDir = label_config.get("Filebot","path")
				db = label_config.get("Filebot","database")
				format = label_config.get("Filebot","format")
				processor.renameAndMove(filebot, processingDir, outputDir, db, format)
				
				action = 'added'					
			# if torrent goes from seeding -> finished, remove torrent from list
			elif torrent_prev == 'seeding' and torrent_state == 'finished':
				processingDir = os.path.normpath(os.path.join(config.get("General","path"), torrent['name']))
				print 'removing processing directory\n'
				if os.path.isdir(processingDir):
					shutil.rmtree(processingDir, ignore_errors=True)
				if config.getboolean("General","remove"):
					print 'removing torrent from uTorrent\n'
					processor.removeTorrent(torrent_hash)
					action = 'removed'
			else:
				print 'torrent has not transitioned to the proper states for processing'
				
			# notify user
			if (action == 'added' and config.getboolean("General","notify")) or (action == 'removed' and config.getboolean("General","notifyRemove")):
				print 'sending notifications'
				print '--'
				notification = {
					'subject': 'autoHTPC Notification',
					'title': torrent['name'],
					'label': torrent['label'],
					'date': time.strftime("%m/%d/%Y"),
					'time': time.strftime("%I:%M:%S%p"),
					'action': action
				}
				if config.getboolean("Email", "enable"):
					print 'sending email'
					email_info = {
						'server': config.get("Email", "SMTPServer"),
						'port': config.get("Email", "SMTPPort"),
						'user': config.get("Email", "username"),
						'pass': config.get("Email", "password"),
						'to': config.get("Email", "emailTo").split('|')
					}
					processor.sendEmail(email_info, notification)
				if config.getboolean("PushBullet", "enable"):
					print 'pushing note'
					token = config.get("PushBullet", "token")
					devices = config.get("PushBullet", "devices").split('|')
					processor.sendPush(token, devices, notification)
				print '--\n'
		else:
			print 'label does not have a config file'
			
		print 'DONE!'
		if config.getboolean("General","pause"):
			raw_input('press enter to continue')
	else:
		print 'autoHTPC received an incorrect amount of arguments'
		raw_input('press enter to continue')