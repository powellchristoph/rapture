# -*- coding: utf-8 -*-
import sys

from setuptools import setup, find_packages

REQUIRES = ['pyrax', 'paramiko']
            
setup(
    name='rapture',
    version='0.1',
    description='Rapture - watches a directory and uploads files to the cloud',
    license='Apache License 2.0',
    url='github.com/powellchristoph/rapture',
    author='Chris Powell',
    author_email='powellchristoph@gmail.com',
    install_requires=REQUIRES,
    test_suite='rapture',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'rapture-app= rapture.app:run',
        ]
    },
#    data_files=[('config', ['etc/rapture.conf', 'ini/configspec.ini'])],
    packages=find_packages(exclude=['tests*', 'deuce/tests*'])
)
