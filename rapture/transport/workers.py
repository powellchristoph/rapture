# workers.py

import logging
import os
import threading

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
    
    chksum = pyrax.utils.get_checksum(filename)
    for i in range(MAX_RETRIES):
        try:
            logger.debug("Starting file transfer to %s." % container_name)
            cf.upload_file(container, filename, etag=chksum)
            logger.debug("Transfer complete.")
            os.remove(filename)
            break
        except pyrax.UploadFailed:
            logger.warning("Upload to container:%s in %s failed, retry %d" % (container_name, region, i))
    else:
        logger.error("Upload to container:%s in %s failed!" % (container_name, region))


def scp_func(settings, filename):
    name = threading.currentThread().getName().upper()
    logger = logging.getLogger(__name__ + "." + name)
    logger.critical("%s has not been implemented." % name)
    raise Exception("Worker not implemented")
