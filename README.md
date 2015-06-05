# Rapture

Monitors a directory for files and uploads them to multiple destinations. Currently supports [Rackspace Cloudfiles](http://www.rackspace.com/cloud/files) or sftp to remote server.

## Installation:
There is an included [upstart file](https://github.com/powellchristoph/rapture/blob/master/etc/upstart/rapture.conf) for Debian/Ubuntu support. The default path to the virtualenv is /srv/rapture, please update it if you install to a different location.
```
git clone https://github.com/powellchristoph/rapture.git /srv/rapture
virtualenv /srv/rapture
cd /srv/rapture
source bin/rapture/activate
pip install -e .
bin/rapture-app
```

## Config:
Configure the [config file](https://github.com/powellchristoph/rapture/blob/master/etc/rapture.conf) with the appropriate values for either your Rackspace Cloud account or the SSH credentials of the server.

### Encryption
#### File decryption
Supports the decryption of files before uploading them to Cloudfiles/SFTP. Currently supports GPG decryption, keys must already exists in *gpghome*. Set the *gpghome* setting to a different path if your keys are not stored in the default location. 
```
# Default is no
enable_decryption = no
```

#### File encryption
Not yet supported

### Compression
#### Compress files
You can compress files before you upload them. Currently only supports gzip compression.
```
# Default is no
enable_compression = no
```

#### Decompress files
Not yet supported
