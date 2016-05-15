# -*- coding: utf-8 -*-

"""Small utilities"""

import errno
import gzip
import logging.config
from logging.handlers import RotatingFileHandler
from optparse import OptionParser
import os
from os.path import join as pjoin, isfile, islink, altsep, sep, isabs, dirname, isdir, normpath, abspath, expanduser, exists, \
    basename
import shlex
from shutil import copy2, rmtree
import signal
import sys
import threading
import time

from decorator import decorator


try:
    from subprocess32 import Popen, PIPE  # pylint: disable=import-error
except ImportError:
    # Thread unsafe
    from subprocess import Popen, PIPE

try:
    from shutil import SpecialFileError
except ImportError:
    SpecialFileError = IOError


__all__ = ['Oscillator', 'LoggingObject', 'Runable', 'monkey_patch_logging', 'locked_method', 'hardlink_r',
           'AdvancedRotatingFileHandler', 'production_run']


SVC_START = 'start'
SVC_STOP = 'stop'
SVC_RESTART = 'restart'
SVC_STATUS = 'status'


class AdvancedRotatingFileHandler(RotatingFileHandler):
    """RotatingFileHandler that can compress rotated logs.
    Currently only compression='.gz' is supported!

    Example configuration to compress rotated logs with .gz:

    [handler_advancedRotatingFileHandler]
    class=s1_cnd_common.tools.AdvancedRotatingFileHandler
    level=DEBUG
    formatter=shorter
    args=('/tmp/testlog.log', 'a', 104857600, 10, None, 0, '.gz')
    """

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0, compression=None):
        """%s


        """ % RotatingFileHandler.__doc__

        RotatingFileHandler.__init__(self, filename=filename, mode=mode, maxBytes=maxBytes,
                                     backupCount=backupCount, encoding=encoding, delay=delay)
        if compression not in (None, '.gz'):
            raise ValueError("Only '.gz' compression is supported.")
        self._compression = compression

    def doRollover(self):
        """
        Do a rollover with compression if specified.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            ext = ''
            if self._compression is not None:
                ext = self._compression
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d%s" % (self.baseFilename, i, ext)
                dfn = "%s.%d%s" % (self.baseFilename, i + 1, ext)
                if os.path.exists(sfn):
                    # print "%s -> %s" % (sfn, dfn)
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.baseFilename, dfn)
            if self._compression is not None:
                with open(dfn, "rb") as file_in:
                    try:
                        # Open output file.
                        file_out = gzip.open(dfn + ext, "wb")
                        # Write output.
                        file_out.writelines(file_in)
                    finally:
                        file_out.close()
                os.remove(dfn)
            # print "%s -> %s" % (self.baseFilename, dfn)
        self.stream = self._open()
