#!/usr/bin/env python
from setuptools import setup

import odk

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'django>=2.2,<4.0',
    'django-braces>=1.11,<2.0',
]

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Framework :: Django',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
]

setup(
    name='django-odk',
    version=odk.__version__,
    description='Django Data Collection tool using ODK Collect mobile App',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/openHBP/django-odk',
    author='Patrick HOUBEN',
    author_email='p.houben@cra.wallonie.be',
    license='GPL-3.0-or-later',
    packages=['odk', 'odk.openrosa'],
    # package_data={'static':['*'], 'templates':['*'], 'templatestags':['*'],},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    platforms=['Linux']
)
