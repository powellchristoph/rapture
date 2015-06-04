import gnupg
import logging
import os
import sys
import time

# TODO: The configuration validation should be replaced with validate

from ConfigParser import SafeConfigParser

def die(msg, ex=None):
    print msg
    if ex:
        print ex
    sys.exit(1)

def validate_config(config_file):
    settings = {}

    parser = SafeConfigParser()
    parser.read(config_file)

    try:
        section = 'app'
        settings[section] = {}
        settings['app']['watch_dir'] = parser.get(section, 'watch_dir')
        settings['app']['scan_interval'] = parser.getint(section, 'scan_interval')
        settings['app']['log_level'] = parser.get(section, 'log_level')
        settings['app']['error_file'] = parser.get(section, 'error_file')
        if parser.has_option(section, 'gpghome'):
            settings['app']['gpghome'] = parser.get(section, 'gpghome')
        else:
            settings['app']['gpghome'] = None
    except Exception, e:
        die('Error in the configuration file.', e)

    def validate_cloudfiles(section):
        try:
            settings[section] = {}
            settings[section]['type'] = parser.get(section, 'type')
            settings[section]['credential_file'] = parser.get(section, 'credential_file')
            settings[section]['container_name'] = parser.get(section, 'container_name')
            settings[section]['region'] = parser.get(section, 'region')
            settings[section]['use_snet'] = parser.getboolean(section, 'use_snet')
        except Exception, e:
            die('Error in the configuration file.', e)

    def validate_scp(section):
        try:
            settings[section] = {}
            settings[section]['type'] = parser.get(section, 'type')
            settings[section]['address'] = parser.get(section, 'address')
            settings[section]['username'] = parser.get(section, 'username')
            if parser.has_option(section, 'password'):
                settings[section]['password'] = parser.get(section, 'password')
            elif parser.has_option(section, 'ssh_key'):
                settings[section]['ssh_key'] = parser.get(section, 'ssh_key')
            else:
                die('Cannot find valid password or ssh_key for %s user' % settings['username'])
        except Exception, e:
            die('Error in the configuration file.', e)

    for section_name in [section for section in parser.sections() if section != 'app']:
        if parser.get(section_name, 'type') == 'cloudfiles':
            validate_cloudfiles(section_name)
        elif parser.get(section_name, 'type') == 'scp':
            validate_scp(section_name)
        else:
            die('Unsupported transport type: %s/%s' % (section_name, parser.get(section_name)))

    return settings

def setup_logging(log_level=logging.INFO):
    LOG_LEVELS = {
            'DEBUG'     : logging.DEBUG,
            'INFO'      : logging.INFO,
            'WARNING'   : logging.WARNING,
            'ERROR'     : logging.ERROR,
            'CRITICAL'  : logging.CRITICAL
    }

    logger = logging.getLogger('rapture')
    logger.setLevel(LOG_LEVELS[log_level])
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def decrypt_file(encrypted_file, gpghome=None):
    '''
    Decrypts the file using the gpg keys found at gpghome. 
    Returns True if successful decryption, else False
    '''
    gpghome = gpghome or os.path.join(os.getenv('HOME'), '.gnupg')
    gpg = gnupg.GPG(gnupghome=gpghome)
    output_filename = os.path.splitext(encrypted_file)[0]
    with open(encrypted_file, 'rb') as f:
        status = gpg.decrypt_file(f, output=output_filename)
    if not status.ok:
        raise Exception('Unable to decrypt file', status.stderr)
    return output_filename

def ready_check(file_list, delay=10):
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
