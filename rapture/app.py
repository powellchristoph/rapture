import logging
import os
import signal
import sys
import time

from rapture import conf
from rapture.util import setup_logging, ready_check, decrypt_file, die
from rapture.transport.manager import TransportManager

from requests.packages import urllib3
urllib3.disable_warnings()

debug = logging.getLogger('rapture').debug
info = logging.getLogger('rapture').info
warning = logging.getLogger('rapture').warning
error = logging.getLogger('rapture').error

def scan(watch_dir):
    debug("Scanning for files.")
    return [os.path.join(watch_dir, f) for f in os.listdir(watch_dir)
            if os.path.isfile(os.path.join(watch_dir, f))
            and not f.startswith('.')]

def shutdown(signum, frame):
    info("Shutting down...")
    sys.exit(0)

def run():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    setup_logging(conf['app']['log_level'])
    watch_dir = conf['app']['watch_dir']
    scan_interval = conf['app']['scan_interval']
    error_file = conf['app']['error_file']
    gpghome = conf['app']['gpghome']

    info('Starting Rapture, watching %s' % watch_dir)
    for setting, value in conf['app'].items():
        debug("{0}:\t{1}".format(setting, value))
    
    tm = TransportManager(error_file)

    while True:
        found_files = scan(watch_dir)
        ready_files = ready_check(found_files)

        # Find and decrypt any gpg files
        encrypted_files = [f for f in ready_files if f.endswith('.gpg')]
        for f in encrypted_files:
            try:
                debug("Decrypting {0}".format(f))
                decrypted_file = decrypt_file(f, gpghome)
                ready_files.remove(f)
                ready_files.append(decrypted_file)
                os.remove(f)
            except Exception as err:
                error("Error decrypting {0}: {1}".format(f, err))
                die('Error decrypting', err)

        tm.transfer(ready_files)
        debug("Sleeping for %d seconds." % scan_interval)
        time.sleep(scan_interval)
