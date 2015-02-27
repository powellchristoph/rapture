# Rapture

Monitors a directory for files and uploads them to multiple destinations. Currently supports [Rackspace Cloudfiles](http://www.rackspace.com/cloud/files) or sftp to remote server.

---

Installation:

```
git clone https://github.com/powellchristoph/rapture.git /srv/rapture
virtualenv /srv/rapture
cd /srv/rapture
source bin/rapture/activate
pip install -e .
bin/rapture-app
```

Configure the [config file](https://github.com/powellchristoph/rapture/blob/master/etc/rapture.conf) with the appropriate values for either your Rackspace Cloud account or the SSH 
credentials of the server.

There is an included [upstart file](https://github.com/powellchristoph/rapture/blob/master/etc/upstart/rapture.conf) for Debian/Ubuntu support. The default path to the virtualenv is /srv/rapture, please update it if you install to a different location.


