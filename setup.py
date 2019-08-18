# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='unitdoc',
    version='0.2.0',
    description='A framework that enables classes that describe physical objects with units and easy serialization.',
    long_description=readme,
    author='Deniz Bozyigit',
    author_email='deniz195@gmail.com',
    url='https://github.com/deniz195/unitdoc',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'examples')),
    install_requires = ['attrs', 'cattrs', 'attr-descriptions>=0.1.3', 'ruamel.yaml', 'pint_mtools'],
    classifiers=[
        'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3',     
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],    
)
