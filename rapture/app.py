import logging
import os
import signal
import sys
import time

from rapture import conf
from rapture.util import setup_logging
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
    setup_logging()
    watch_dir = conf['app']['watch_dir']
    scan_interval = conf['app']['scan_interval']
    
    info('Starting Rapture, watching %s' % watch_dir)
    tm = TransportManager()

    while True:
        found_files = scan(watch_dir)
        tm.transfer(found_files)
        debug("Sleeping for %d seconds." % scan_interval)
        time.sleep(scan_interval)
