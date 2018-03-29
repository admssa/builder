import constants as config
import os
import logging
from logging.handlers import TimedRotatingFileHandler

from coralogix.coralogix_logger import CoralogixLogger


def create_logger(app):
    """
    Creates a rotating log based on configuration values
    """

    # Create our logger
    logger = logging.getLogger(config.LOGGER_NAME)

    # Configure Coralogix and add handler
    if config.CORALOGIX_ENABLED:
        create_coralogix_logger(logger, app)

    else:
        create_file_logger(logger, app)

    logger.info("Starting Logger: %s.", config.LOGGER_NAME)

    return logger


def create_coralogix_logger(logger, app):
    """
    Adds the Coralogix log handler to logging so that
    logs are sent to Coralogix.
    """

    CoralogixLogger.configure(config.CORALOGIX_PRIVATE_KEY,
                              config.CORALOGIX_APP_NAME,
                              config.CORALOGIX_SUB_SYSTEM)

    coralogix_logger = CoralogixLogger.get_logger(config.CORALOGIX_SUB_SYSTEM)
    coralogix_logger.setLevel(config.LOGGING_SEVERITY)

    logger.addHandler(coralogix_logger)
    logger.setLevel(config.LOGGING_SEVERITY)

    app.logger.addHandler(coralogix_logger)
    app.logger.setLevel(config.LOGGING_SEVERITY)


def create_file_logger(logger, app):
    """
    Adds the file handler to logging so that logs are saved to the
    file system.
    """

    # Define our path and create if necessary
    log_path = os.path.join(config.LOG_FILE_ROOT, config.LOG_FILE_PREFIX)
    os.makedirs(config.LOG_FILE_ROOT, exist_ok=True)

    # add a timed rotating handler
    handler = TimedRotatingFileHandler(log_path,
                                       when=config.LOG_ROTATE_WHEN,
                                       interval=config.LOG_ROTATE_INTERVAL,
                                       backupCount=config.LOG_FILE_NUM_BACKUPS)

    handler.setLevel(config.LOGGING_SEVERITY)

    handler.setFormatter(logging.Formatter(fmt=config.LOG_DEFAULT_FORMAT,
                                           datefmt=config.LOG_DEFAULT_DATE_FORMAT,
                                           style="{"))

    # Add handlers to both the default and Flask handlers
    logger.addHandler(handler)
    logger.setLevel(config.LOGGING_SEVERITY)
    app.logger.addHandler(handler)
    app.logger.setLevel(config.LOGGING_SEVERITY)


def get_default_logger():
    """
    Returns the default logger
    """

    logger = logging.getLogger(config.LOGGER_NAME)

    return logger
