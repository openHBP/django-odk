#!/usr/bin/env python
from setuptools import setup

import django_odk


with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'django>=2.2,<4.0',
    'django-braces>=1.11,<2.0',
    'pyxform>=1.10.0,<2.0',
    'xlsconv>=1.3.0,<2.0',
    'pillow>=9.1.1,<9.9',
    'lxml>=4.9.0,<9.0.0',
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
    version=django_odk.__version__,
    description='Django Data Collection tool using ODK Collect mobile App',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/openHBP/django-odk',
    author='Patrick HOUBEN',
    author_email='p.houben@cra.wallonie.be',
    license='GPL-3.0-or-later',
    packages=['odk', 'odk.openrosa', 'odk.locale', 'odk.migrations', 'odk.templates', 'odk.templatetags',
        'odkdata', 'odkdata.models', 'odkdata.migrations'],
    package_dir={"":"django_odk"},
    package_data={'xform_sample':['*'], 'doc':['*'],},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    platforms=['Linux']
)
