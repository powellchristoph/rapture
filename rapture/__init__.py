"""
Rapture Global
"""

import os
import sys

from rapture.util import validate_config

CONFIG_FILENAME = 'rapture.conf'
CONFIG_DIR = os.path.join(sys.prefix, 'etc')

candidate_paths = [
    os.path.join('/etc/rapture', CONFIG_FILENAME),
    os.path.join(CONFIG_DIR, CONFIG_FILENAME),
    os.path.join(os.path.abspath('etc'), CONFIG_FILENAME)
]

def find_config_file():
    global candidate_paths

    chosen = None

    for candidate in candidate_paths:
        if os.path.exists(candidate):
            chosen = candidate
            break

    if chosen is None:
        sys.stderr.write("FATAL ERROR: could not locate a config file:\n")

        for p in candidate_paths:
            sys.stderr.write("{0}\n".format(p))

        sys.exit(1)

    return chosen

config_file = find_config_file()

conf = validate_config(config_file)
