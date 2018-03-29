
from __future__ import print_function
import time
import requests
from . import Coralogix
from httplib2 import Http
from threading import Lock
from coralogix.debug_logger import DebugLogger

try:
    import ujson as json
    print("httpsender.py: Using ujson library for JSON parsing (compiled in C)")
except Exception:
    import json
    print("httpsender.py: Using standard library for JSON parsing (interpreted in Python)")


class CoralogixHTTPSender(object):
    _mutex = Lock()
    _http = False

    @classmethod
    def _init(cls, timeout=None):
        timeout = timeout or Coralogix.HTTP_TIMEOUT
        try:
            DebugLogger.debug("Creating Http object")
            cls._http = Http(timeout=timeout, disable_ssl_certificate_validation=True)
        except Exception as e:
            cls._http = False
            DebugLogger.exception("Failed to create Http object", e)

    @classmethod
    def send_request(cls, bulk):
        try:
            cls._mutex.acquire()
            attempt = 0
            while attempt < Coralogix.HTTP_SEND_RETRY_COUNT:
                try:
                    if not cls._http:
                        cls._init()
                    DebugLogger.info("About to send bulk to Coralogix server. Attempt number: {}".format(attempt + 1))
                    # res = requests.post(Coralogix.CORALOGIX_LOG_URL, timeout=Coralogix.HTTP_TIMEOUT, json=bulk)
                    res, content = cls._http.request(uri=Coralogix.CORALOGIX_LOG_URL, method='POST', headers={'Content-Type': 'application/json; charset=UTF-8'}, body=json.dumps(bulk))
                    DebugLogger.info("Successfully sent bulk to Coralogix server. Result is: {}".format(res.status))
                    return
                except Exception as e:
                    DebugLogger.exception("Failed to send http post request", e)
                attempt += 1
                DebugLogger.error("Failed to send bulk. Will retry in: {} seconds...".format(Coralogix.HTTP_SEND_RETRY_INTERVAL))
                time.sleep(Coralogix.HTTP_SEND_RETRY_INTERVAL)
        except Exception as e:
            DebugLogger.exception("Failed to send http post request", e)
        finally:
            if cls._mutex:
                cls._mutex.release()

    @classmethod
    def get_time_sync(cls):
        """ A helper method to get Coralogix server current time and calculate the time difference """
        try:
            cls._mutex.acquire()
            # if not cls._http:
            #     cls._init()
            DebugLogger.info("Syncing time with coralogix server")
            response = requests.get(Coralogix.CORALOGIX_TIME_DELTA_URL, timeout=Coralogix.TIME_DELAY_TIMEOUT)
            if response and response.status_code == 200:
                server_time = int(response.content.decode()) / 1e4  # Server epoch time in milliseconds
                local_time = time.time() * 1e3  # Local epoch time in milliseconds
                time_delta = server_time - local_time
                DebugLogger.info("Server epoch time= {}, local epoch time= {}; Updating time delta to: {}".format(server_time, local_time, time_delta))
                return True, time_delta
            # res, content = cls._http.request(Coralogix.CORALOGIX_TIME_DELTA_URL)
            # if res and res.status == 200:
            #     # Get server ticks from 1970
            #     server_time = int(content) / 10000  # Relative to 1970
            #     local_time = int(time.time() * 1000)
            #
            #     time_delta = server_time - local_time
            #     DebugLogger.info("Updating time delta to: {}".format(time_delta))
            #     return True, time_delta
            return False, 0
        except Exception as e:
            DebugLogger.exception("Failed to send http get request", e)
        finally:
            if cls._mutex:
                cls._mutex.release()
