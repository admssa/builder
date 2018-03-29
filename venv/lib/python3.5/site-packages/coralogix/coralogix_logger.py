
from __future__ import print_function
from . import Coralogix
from logging import Handler
from threading import current_thread
from coralogix.manager import LoggerManager
from coralogix.debug_logger import DebugLogger


class CoralogixLogger(Handler):

    """
    Coralogix logger main class. This class send logs to Coralogix server.
    It is possible to use this class as a handler for the standard Python logger.
    """

    def __init__(self, private_key=None, app_name=None, subsystem=None, category=None, sync_time=False):
        self.configure(private_key, app_name, subsystem, sync_time)
        self._category = category if category is not None else Coralogix.CORALOGIX_CATEGORY
        Handler.__init__(self)

    @classmethod
    def set_debug_mode(cls):
        """ Enable debug mode; prints internal log messages to stdout """
        DebugLogger.debug_mode = True

    def emit(self, record):
        self.log(Coralogix.map_severity(record.levelno),
                 self.format(record),
                 record.name,
                 record.module,
                 record.funcName,
                 record.thread)

    @classmethod
    def configure(cls, private_key, app_name, sub_system, sync_time=False):
        """ Configure Coralogix logger with customer specific values """
        if not LoggerManager.configured:
            private_key = private_key if private_key and (not private_key.isspace()) else Coralogix.FAILED_PRIVATE_KEY
            app_name = app_name if app_name and (not app_name.isspace()) else Coralogix.NO_APP_NAME
            sub_system = sub_system if sub_system and (not sub_system.isspace()) else Coralogix.NO_SUB_SYSTEM
            LoggerManager.configure(sync_time=sync_time, privateKey=private_key, applicationName=app_name, subsystemName=sub_system)

    @classmethod
    def get_logger(cls, name=Coralogix.CORALOGIX_CATEGORY):
        """ Return a new instance of CoralogixLogger """
        if LoggerManager.configured:
            return CoralogixLogger(category=name)

    def log(self, severity, message, category=None, classname="", methodname="", thread_id=""):
        """ Logs a message on this logger """
        category = category if category else self._category
        thread_id = str(thread_id)
        thread_id = thread_id if thread_id and (not thread_id.isspace()) else current_thread().ident
        LoggerManager.add_logline(message, severity, category, className=classname, methodName=methodname, threadId=thread_id)

    def debug(self, message, category=None, classname="", methodname="", thread_id=""):
        """ Logs a message with level DEBUG on this logger. """
        self.log(Coralogix.Severity.DEBUG, message, category, classname, methodname, thread_id)

    def verbose(self, message, category=None, classname="", methodname="", thread_id=""):
        """ Logs a message with level VERBOSE on this logger. """
        self.log(Coralogix.Severity.VERBOSE, message, category, classname, methodname, thread_id)

    def info(self, message, category=None, classname="", methodname="", thread_id=""):
        """ Logs a message with level INFO on this logger. """
        self.log(Coralogix.Severity.INFO, message, category, classname, methodname, thread_id)

    def warning(self, message, category=None, classname="", methodname="", thread_id=""):
        """ Logs a message with level WARNING on this logger. """
        self.log(Coralogix.Severity.WARNING, message, category, classname, methodname, thread_id)

    def error(self, message, category=None, classname="", methodname="", thread_id=""):
        """ Logs a message with level ERROR on this logger. """
        self.log(Coralogix.Severity.ERROR, message, category, classname, methodname, thread_id)

    def critical(self, message, category=None, classname="", methodname="", thread_id=""):
        """ Logs a message with level CRITICAL on this logger. """
        self.log(Coralogix.Severity.CRITICAL, message, category, classname, methodname, thread_id)

    @staticmethod
    def flush_messages():
        LoggerManager.flush()
