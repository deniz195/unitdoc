# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='unitdoc',
    version='0.1.2',
    description='A framework that enables classes that describe physical objects with units and easy serialization.',
    long_description=readme,
    author='Deniz Bozyigit',
    author_email='deniz195@gmail.com',
    url='https://github.com/deniz195/unitdoc',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
    install_requires = ['attr', 'cattrs', 'ruamel.yaml', 'pint_mtools', 'pytest']
)
