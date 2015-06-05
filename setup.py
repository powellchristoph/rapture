# -*- coding: utf-8 -*-
import sys

from setuptools import setup, find_packages

REQUIRES = ['pyrax', 'paramiko', 'python-gnupg']
            
setup(
    name='rapture',
    version='0.1.0',
    description='Rapture - watches a directory and uploads files to the cloud',
    license='Apache License 2.0',
    url='github.com/powellchristoph/rapture',
    author='Chris Powell',
    author_email='powellchristoph@gmail.com',
    install_requires=REQUIRES,
    #test_suite='rapture',
    #zip_safe=False,
    entry_points={
        'console_scripts': [
            'rapture-app= rapture.app:run',
        ]
    },
)
