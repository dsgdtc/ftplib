import logging
import logging.config


class LogObject(object):
	def __init__(self):
		CONF_LOG='/root/script/ftplib/etc/mylog.config'
		logging.config.fileConfig(CONF_LOG)
		self.logger = logging.getLogger()
#log=LogObject()
