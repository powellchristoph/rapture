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
        'local': local_move_func,
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

    def transfer(self, file_list):
        """
        Executes the file transfer for the given methods.
        """

        self.load_errors()
        for filename in file_list:
            # If there was a previous error, retry only the failed workers
            if filename in self.errors.keys():
                failed_workers = self.errors[filename]
                self.logger.warning("Found previous error, retrying %s with %s drivers." % (filename, ','.join(failed_workers)))
                self.execute(filename, failed_workers)
            else:
                self.execute(filename, self.all_workers)

        self.dump_errors()

    def execute(self, filename, workers):
        results = []
        for d in workers:
            worker = threading.Thread(
                    name=d,
                    target=WORKER_FUNCTIONS.get(conf[d]['type']),
                    args=(conf[d], filename, results))
            worker.start()
            self.threads.append(worker)

        for t in self.threads:
            t.join()

        if results:
            # Write out any errors to self.error_file
            self.logger.warning("Errors found for %s" % filename)
            self.errors[filename] = results
        else:
            # Transfer was successful, delete the file
            self.logger.info("{0} completed.".format(filename))
            self.errors.pop(filename, None)
            os.remove(filename)

    def dump_errors(self):
        # Writes out the errors to the error_file
        with open(self.error_file, 'w') as outfile:
            json.dump(self.errors, outfile, sort_keys=True)
            self.logger.debug("Dumping errors:")
            self.logger.debug(self.errors)

    def load_errors(self):
        # Loads the errors from the error_file
        if not os.path.exists(self.error_file):
            # Create an empty file
            with open(self.error_file, 'w') as f:
                d = {}
                json.dump(d, f)

        with open(self.error_file) as infile:
            self.errors = json.load(infile)
            self.logger.debug("Loaded errors:")
            self.logger.debug(self.errors)
