# workers.py

import logging
import os
import shutil
import threading
import time

import pyrax
pyrax.set_setting("identity_type", "rackspace")

import paramiko

MAX_RETRIES = 5

def local_move_func(settings, filename, results):
    """
    Moves files to a local directory. Useful for testing.
    """
    name = threading.currentThread().getName()
    logger = logging.getLogger(__name__ + "." + name)
    destination = settings['destination']

    try:
        if not os.path.exists(destination):
            logger.info("{0} does not exist, creating now...".format(destination))
            os.makedirs(destination)
    except:
        logger.critical("Unable to make {0}! Skipping...".format(destination))
        results.append(name)

    try:
        new_filename = os.path.join(settings['destination'], os.path.basename(filename))
        logger.debug("Moving {0} to {1}".format(filename, new_filename))
        shutil.copyfile(filename, new_filename)
    except:
        logger.error("{0} failed...".format(filename))
        results.append(name)

def cloudfiles_func(settings, filename, results):
    """
    Uploads files to Rackspace Cloud Files.
    """

    name = threading.currentThread().getName()
    logger = logging.getLogger(__name__ + "." + name)

    creds_file = settings['credential_file']
    pyrax.set_credential_file(creds_file)
    pyrax.set_setting('use_servicenet', settings['use_snet'])
    region = settings['region']
    container_name = settings['container_name']

    try:
        cf = pyrax.connect_to_cloudfiles(region=region)
        container = cf.get_container(container_name)
    except:
        logger.error("Unable to connect to cloudfiles. Transfer for {0} aborted, failing gracefully.".format(filename))
        results.append(name)
        return

    if os.path.getsize(filename) >= 5368709120:
        logger.error("{0} is too large. Files over 5GB are not currently supported.".format(filename))
        results.append(name)
        return
    
    chksum = pyrax.utils.get_checksum(filename)
    for i in range(MAX_RETRIES):
        try:
            start = time.time()
            #Used for testing the retry
            #raise pyrax.exceptions.UploadFailed()
            cf.upload_file(container, filename, etag=chksum)
            end = time.time()
            logger.debug("%s transferred to %s in %.2f secs." % (filename, container_name, (end - start)))
            break
        except pyrax.exceptions.UploadFailed:
            logger.warning("Upload to container:%s in %s failed, retry %d" % (container_name, region, i + 1))
            time.sleep(2)
    else:
        logger.error("Upload to container:%s in %s failed!" % (container_name, region))
        results.append(name)


def scp_func(settings, filename, results):
    """
    Transfers files to a server via scp/sftp.
    """

    name = threading.currentThread().getName()
    logger = logging.getLogger(__name__ + "." + name)

    address = settings['address']
    username = settings['username']
    port = settings.get('port', 22)

    if 'password' in settings.keys():
        password = settings['password']
    else:
        ssh_key = settings['ssh_key']

    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        s.connect(address, port, username=username, password=password, timeout=4)
        sftp = s.open_sftp()
    except Exception as e:
        results.append(name)
        return

    for i in range(MAX_RETRIES):
        try:
            start = time.time()
            sftp.put(filename, os.path.basename(filename))
            end = time.time()
            logger.debug("Tranfer completed in %.2f secs" % (end - start))
            break
        except Exception as e:
            logger.warning("Upload to server:%s failed, retry %d" % (container_name, i + 1))
            time.sleep(2)
    else:
        logger.error("Upload to server:%s failed!" % (container_name))
        results.append(name)
