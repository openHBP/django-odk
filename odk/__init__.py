"""
See PEP 386 (https://www.python.org/dev/peps/pep-0386/)
Release logic:
 1. Increase version number (change __version__ below).
 2. Check that all changes have been documented in CHANGELOG.rst.
 3. git add filer/__init__.py CHANGELOG.rst
 4. git commit -m 'Bump to {new version}'
 5. git push
 6. git tag {new version}
 7. git push --tags
 8. python setup.py sdist bdist_wheel
 9. twine upload dist/django-filer-{new version}.tar.gz
"""

__version__ = "0.2.6"
__author__ = 'Patrick HOUBEN'
__credits__ = 'Walloon Agricultural Research Centre'
