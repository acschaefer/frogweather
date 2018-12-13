#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup module for the frogweather package

This module configures setuptools so that it can create a distribution for the
package.
"""

# Import required standard libraries.
import io
import os
import setuptools

# Load the readme.
maindir = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(maindir, 'README.md'), encoding='utf-8') as file:
    readme = file.read()

# Configure setuptools.
setuptools.setup(name='frogweather',
                 version='0.5',
                 description='Frog-themed weather station',
                 long_description=readme,
                 long_description_content_type='text/markdown',
                 license='MIT',
                 url='https://github.com/acschaefer/frogweather',
                 author='Alexander Schaefer',
                 author_email='acschaefer@users.noreply.github.com',
                 maintainer='Alexander Schaefer',
                 include_package_data=False,
                 packages=['frogweather'],
                 install_requires = [
                     'darkskylib', 
                     'PyYAML',
                     'pygame',
                     'duallog'],
                 classifiers=[
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Operating System :: OS Independent']
)
