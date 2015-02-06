# workers.py

import logging
import os
import threading
import time

import pyrax
pyrax.set_setting("identity_type", "rackspace")

MAX_RETRIES = 5

def cloudfiles_func(settings, filename):
    name = threading.currentThread().getName().upper()
    logger = logging.getLogger(__name__ + "." + name)

    creds_file = settings['credential_file']
    pyrax.set_credential_file(creds_file)
    region = settings['region']
    container_name = settings['container_name']
    cf = pyrax.connect_to_cloudfiles(region=region)

    container = cf.get_container(container_name)

    if os.path.getsize(filename) >= 5368709120:
        logger.error("File too large. Files over 5GB are not currently supported.")
        return
    
    chksum = pyrax.utils.get_checksum(filename)
    for i in range(MAX_RETRIES):
        try:
            start = time.time()
            cf.upload_file(container, filename, etag=chksum)
            end = time.time()
            logger.debug("Transfer complete in %.2f secs." % (end - start))
            os.remove(filename)
            break
        except pyrax.exceptions.UploadFailed:
            logger.warning("Upload to container:%s in %s failed, retry %d" % (container_name, region, i))
            time.sleep(2)
    else:
        logger.error("Upload to container:%s in %s failed!" % (container_name, region))


def scp_func(settings, filename):
    name = threading.currentThread().getName().upper()
    logger = logging.getLogger(__name__ + "." + name)
    logger.critical("%s has not been implemented." % name)
    raise Exception("Worker not implemented")
