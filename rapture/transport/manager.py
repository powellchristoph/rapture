import logging
import threading
import time

from rapture import conf
from rapture.transport.workers import *

DRIVER_FUNCTIONS = {
        'cloudfiles': cloudfiles_func,
        'scp': scp_func,
    }

class TransportManager(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.drivers = [d for d in conf.keys() if d is not 'app']
        self.logger.debug("TransportManager created with %s drivers." % ",".join(self.drivers))
        self.threads = []

    def check_files(self, file_list, delay=10):
        if not file_list:
            return []
        self.logger.debug("Starting file readiness check.")
        ready_files = []
        tmp = {}

        def get_last_byte(filename):
            with open(filename, 'rb') as f:
                f.seek(0, 2)
                return f.tell()
    
        for filename in file_list:
            tmp[filename] = get_last_byte(filename)

        time.sleep(delay)

        for filename in file_list:
            if tmp[filename] == get_last_byte(filename):
                ready_files.append(filename)

        return sorted(ready_files)

    def transfer(self, file_list):
        for file_ in self.check_files(file_list):
            self.logger.info("Transferring %s" % file_)
            for d in self.drivers:
                driver = threading.Thread(
                        name=d,
                        target=DRIVER_FUNCTIONS[d],
                        args=(conf[d], file_))
                driver.start()
                self.threads.append(driver)

            for t in self.threads:
                t.join()
