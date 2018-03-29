
from __future__ import print_function
import sys
import datetime
import traceback


class DebugLogger(object):
    """ A private class to print debugging messages """
    debug_mode = False

    @classmethod
    def log(cls, lvl, msg, exc=None):
        """ Logs a message with integer level lvl on this logger """
        if not cls.debug_mode:
            return
        try:
            if exc:
                print("{} - [{}]\t-\t{}\nEXCEPTION: {}".format(datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'), lvl, msg, exc))
                traceback.print_exc(file=sys.stdout)
            else:
                print("{} - [{}]\t-\t{}".format(datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'), lvl, msg))
        except Exception as ex:
            if cls.debug_mode:
                print("Failed to print log: {}".format(ex))

    @classmethod
    def debug(cls, msg):
        """ Logs a message with level DEBUG on this logger """
        cls.log("DEBUG", msg)

    @classmethod
    def info(cls, msg):
        """ Logs a message with level INFO on this logger """
        cls.log("INFO", msg)

    @classmethod
    def warning(cls, msg):
        """ Logs a message with level WARNING on this logger """
        cls.log("WARNING", msg)

    @classmethod
    def error(cls, msg):
        """ Logs a message with level ERROR on this logger """
        cls.log("ERROR", msg)

    @classmethod
    def exception(cls, msg, ex=None):
        """ Logs an exception with level ERROR on this logger """
        cls.log("ERROR", msg, exc=ex)
