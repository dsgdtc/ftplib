# -*- coding: utf-8 -*-
'''
@author: guyu<fangcun727@aliyun.com>
This is a safe ftp client. ".tmp" files will be created when geting/sending files
'''
import os
import ftplib
import logging
import socket
from logobject import LogObject

#__all__ = ['FtpClient', 'FtpType']

#FtpType = Enum('SEND', 'GET') # use this as a flag 

TMPFLAG = '.tmp'
TIMEOUT = 2

class FtpClient(LogObject):
	def __init__(self):
		self.host = ''
		self.username = ''
		self.password = ''
		self.timeout = ''
		self.port = ''
		self.ftp = None
		LogObject.__init__(self)
		
	def login_ftp(self, host, username, password, timeout=TIMEOUT, port=21):
		self.logger.info("I am %s", __name__)
		if self.ftp is not None:
			self.logger.warn("Already login, please logout first")
			return False

		self.host = host
		self.username = username
		self.password = password
		self.timeout = timeout
		self.port = port

		try:
			self.ftp = ftplib.FTP()
			self.ftp.connect(host, port, timeout)
			self.ftp.login(username, password)
#			print self.ftp.getwelcome()
#			self.ftp.retrlines('LIST')
#			self.ftp.cwd("/atpcotest/lajfdlkafdsa")
#			self.ftp.rename("incoming2", "./incoming4/sita")
#			self.ftp.mkd("/atpcotest/lalala")
#			print self.ftp.pwd()

		except ftplib.all_errors as e:
			self.logger.error("Login error: %s", e)
			return False
		self.logger.info("Login %s@%s", username, host)
		return True

	def logout_ftp(self):
		if self.ftp is not None:
			try:
				self.ftp.quit()
			except ftplib.all_errors as e:
				self.logger.warn("Abnormal exit: %s",e)
				return False
			self.ftp = None
			self.logger.info("Logout ")
			return True
	def put_file(self, localfile, remotefile_prefix=''):
		"""
		using .tmp model
		"""
		try:
			file = open(localfile, 'rb')
		except IOError as e:
			self.logger.warn("Can not open file: %s. excpet:%s" % (localfile, e))
			return False

		filename = os.path.basename(localfile)
		tmpfilename = filename + TMPFLAG 
		try:
			self.ftp.storbinary("STOR %s" % tmpfilename, file, 8192)
			self.logger.info("successful put file %s" % (localfile))
		except ftplib.all_errors as e:
			self.logger.warn("Can not put file %s,except: %s" % (localfile, e))
		file.close()
		self.ftp.rename(tmpfilename, remotefile_prefix+filename)

		return True
			
	def get_file(self, remotefile, localfile_prefix=''):
		"""
		using .tmp model
		这里应该可以把路径给加上
		"""
		tmpfilename = remotefile + TMPFLAG
		file = open(tmpfilename, 'wb')
		try:
			self.ftp.retrbinary("RETR %s" % remotefile, file.write)
			self.logger.info("successful get file %s" % (remotefile))
		except ftilib.all_errors as e:
			self.logger.warn("Can not get file %s from %s,except: %s" % (remotefile, self.host, e))
			return False
		file.close()
		os.rename(tmpfilename, localfile_prefix+remotefile)
		return True

ftpclient = FtpClient()
ftpclient.login_ftp("172.30.25.84","ftpsched","123456",3)
ftpclient.put_file("/root/script/ftplib/abc","my_")
ftpclient.get_file("bbb","my_")
ftpclient.logout_ftp()
