import json
import logging
import threading
import time

from rapture import conf
from rapture.transport.workers import *

# Worker/function map
WORKER_FUNCTIONS = {
        'cloudfiles': cloudfiles_func,
        'scp': scp_func,
    }

class TransportManager(object):
    """
    The Transport Manager transfers the given files with the configured workers. It 
    handles the threading of the workers and their success/failure. If a transfer 
    fails, it maintains a list of the failed workers and will retry only the failures.

    It also performs a file check on all files to ensure that the file is not being
    actively written too.
    """

    def __init__(self, error_file=None):
        self.logger = logging.getLogger(__name__)
        self.error_file = error_file
        self.all_workers= [d for d in conf.keys() if d is not 'app']
        self.logger.debug("TransportManager created with %s workers." % ",".join(self.all_workers))
        self.threads = []
        self.errors = {} 
        # { '/path/to/file': [wroker1, worker4] }

    def check_files(self, file_list, delay=10):
        """
        Performs a check against the given files to ensure they are not actively being
        written.
        """

        if not file_list:
            return []
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
            last_byte = get_last_byte(filename)
            if tmp[filename] == get_last_byte(filename):
                ready_files.append(filename)

        return sorted(ready_files)

    def transfer(self, file_list):
        """
        Executes the file transfer for the given methods.
        """

        # Validate files are finished transferring
        ready_files = self.check_files(file_list)

        if not ready_files:
            return

        for filename in ready_files:
            self.logger.info("Transferring %s" % filename)

            # If there was a previous error, retry only the failed workers
            self.load_errors()
            if filename in self.errors.keys():
                failed_workers = self.errors[filename]
                self.logger.warning("Found previous error, retrying %s with %s drivers." % (filename, ','.join(failed_workers)))
                self.execute(filename, failed_workers)
            else:
                self.execute(filename, self.all_workers)

    def execute(self, filename, workers):
        results = []
        for d in workers:
            worker = threading.Thread(
                    name=d,
                    target=WORKER_FUNCTIONS[d],
                    args=(conf[d], filename, results))
            worker.start()
            self.threads.append(worker)

        for t in self.threads:
            t.join()

        if results:
            # Write out any errors to self.error_file
            self.errors[filename] = results
            self.dump_errors()
        else:
            # Transfer was successful, delete the file
            os.remove(filename)

    def dump_errors(self):
        # Writes out the errors to the error_file
        with open(self.error_file, 'w') as outfile:
            json.dump(self.errors, outfile, sort_keys=True)

    def load_errors(self):
        # Loads the errors from the error_file
        if not os.path.exists(self.error_file):
            # Create an empty file
            with open(self.error_file, 'w') as f:
                d = {}
                json.dump(d, f)

        with open(self.error_file) as infile:
            self.errors = json.load(infile)
