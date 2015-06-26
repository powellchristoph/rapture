# Rapture

Monitors a directory for files and uploads them to multiple destinations. Currently supports [Rackspace Cloudfiles](http://www.rackspace.com/cloud/files) or sftp to remote server.

## Installation:
There is an included [upstart file](https://github.com/powellchristoph/rapture/blob/master/etc/upstart/rapture.conf) for Debian/Ubuntu support. The default path to the virtualenv is /srv/rapture, please update it if you install to a different location.
```
git clone https://github.com/powellchristoph/rapture.git /srv/rapture
virtualenv /srv/rapture
cd /srv/rapture
source bin/activate
pip install -e .
bin/rapture-app
```

## Build
```
git clone https://github.com/powellchristoph/rapture.git rapture-build
virtualenv rapture-build
cd rapture-build
source bin/activate
pip install wheel
python setup.py bdist_wheel

# Resulting file in dist
rapture-0.1.0-py2.py3-none-any.whl
```

## General Config:
Configure the [config file](https://github.com/powellchristoph/rapture/blob/master/etc/rapture.conf) with the appropriate values for either your Rackspace Cloud account or the SSH credentials of the server.

Each destination is given its own block in the config file.
```
[app]
# Directory that Rapture watches for files
watch_dir = /path/to/watch

# Interval in which Rapture scans for new files in the watch_dir
scan_interval = 60

# Logging level of Rapture
log_level = DEBUG

# Path to the file that Rapture uses to save errors
error_file = /root/.rapture

# Supports the decryption of files before uploading them. 
# Currently supports GPG decryption, keys must already exists in gpghome. Set the gpghome setting 
# to a different path if your keys are not stored in the default location. 
# Default = no [OPTIONAL]
enable_decryption = no
gpghome = /root/.gnupg

# CURRENTLY NOT SUPPORTED
# Supports the encryption of files before uploading them.
# Default = no [OPTIONAL]
enable_encryption = no

# Compress files
# You can compress files before you upload them. Currently only supports gzip compression.
# Default = no [OPTIONAL]
enable_compression = no

# CURRENTLY NOT SUPPORTED
# Decompress files prior to uploading.
# Default = no
enable_decompression = no
```

## Cloudfiles Config:
Cloudfiles specific configuration values
```
# Type of transport [REQUIRED]
type = cloudfiles

# Path to credentials file [REQUIRED]
credential_file = /path/to/rax/creds

# Container that files will be uploaded, must exist prior [REQUIRED]
container_name = example

# Region container resides [REQUIRED]
region = IAD

# Use Rackspace SNET for file uploads [REQUIRED]
# If set to no, your public interface will be used which could 
# incur additional bandwidth charges
use_snet = yes

# Create a nested directory structure based on the file's last modified time.
# Set to year/month/day/filename.txt [OPTIONAL]
# Default is no
nest_by_timestamp = no

# Sets a TTL in seconds on the uploaded object. Cloudfiles will automatically remove
# it when the TTL expires. [OPTIONAL]
# Default is no TTL
set_ttl = 600
```

## SCP Config:
SCP specific configuration values
```
# Type of transport [REQUIRED]
type = scp

# Address of server to transfer the file [REQUIRED]
address = 1.2.3.4

# Username for user on the server [REQUIRED]
username = <username>

# You can use either a password or SSH key for authentication,
# but not both
password = <password>
ssh_key = <ssh_public_key>

# Port that SSH is running on [OPTIONAL]
# Default is 22
port = 22
```

## Local Config:
This worker is for local filesystem moves or testing. The 'local' move could be a remote mounted filesystem.
```
# Type of transport [REQUIRED]
type = local

# Filesystem destination [REQUIRED]
# It will attempt to create the directory if it does not exist.
destination = /path/to/move/file
```


