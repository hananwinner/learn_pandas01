import logging
import os
import inspect

import logging
import sys

_logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
_logger.setLevel(logging.DEBUG)


class LogWrapper():

    def __init__(self, logger):
        self.logger = logger

    def info(self, *args, sep=' '):
        self.logger.info(sep.join("{}".format(a) for a in args))

    def debug(self, *args, sep=' '):
        self.logger.debug(sep.join("{}".format(a) for a in args))

    def warning(self, *args, sep=' '):
        self.logger.warning(sep.join("{}".format(a) for a in args))

    def error(self, *args, sep=' '):
        self.logger.error(sep.join("{}".format(a) for a in args))

    def critical(self, *args, sep=' '):
        self.logger.critical(sep.join("{}".format(a) for a in args))

    def exception(self, *args, sep=' '):
        self.logger.exception(sep.join("{}".format(a) for a in args))

    def log(self, *args, sep=' '):
        self.logger.log(sep.join("{}".format(a) for a in args))


def make_logger(log_arg, log_level, clear_file=False):
    if log_arg is not None:
        if type(log_arg) == str:
            # then its a folder path
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            _, fname = os.path.split(calframe[1][1])
            logger_name, _ = fname.split(sep='.')
            logger = logging.getLogger(logger_name)
            fpath = os.path.join(log_arg, logger_name + '.log')
            with open(fpath, "w"):
                pass
            fh = logging.FileHandler(fpath)
            fh.setLevel(log_level or logging.INFO)
            logger.addHandler(fh)
            logger.setLevel(log_level or logging.INFO)
            return LogWrapper(logger)
        else:
            # its a logger object, just use it
            return log_arg
    else:
        return logging.getLogger('dummy')