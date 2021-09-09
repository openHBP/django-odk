import django_odk
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='django-odk',
    version=django_odk.__version__,   
    description='Django Data Collection tool using ODK Collect mobile App',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/openHBP/django-odk',
    author='Patrick HOUBEN',
    author_email='p.houben@cra.wallonie.be',
    license='Apache License 2.0',
    packages=['django_odk'],
    install_requires=['django',
                      'django-braces',
                      'lxml'
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    platforms=['Linux']
)
