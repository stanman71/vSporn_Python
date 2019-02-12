# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='vSporn-Python',
    version='1.0.0',
    description='Package to management Juniper devices and build topologies in VMware',
    long_description=readme,
    author='Martin Stan',
    author_email='martin.stan@gmx.de',
    url='https://github.com/stanman71/vSporn_Python',
    license=license,
    packages=find_packages(exclude=('CONFIG', 'TOPOLOGIES'))
)
