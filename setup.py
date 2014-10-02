# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

def get(fname):
    try:
        with open(fname) as f:
            return f.read()
    except IOError:  # probably in tox
        return ''

setup(
    name='migrate',
    version=get('VERSION'),
    description='generic migration provider',
    long_description=get('README.rst'),
    author='Brian Hicks',
    author_email='brian@brianthicks.com',
    url='https://github.com/brianhicks/migrate',
    license=get('VERSION'),
    packages=find_packages(exclude=['tests'])
)
