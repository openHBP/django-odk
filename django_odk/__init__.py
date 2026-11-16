"""
Release logic (version lives in pyproject.toml):
 1. uv version --bump patch   (or minor / major)
 2. Check that all changes have been documented in CHANGELOG.rst.
 3. git commit -am "Bump to $(uv version --short)"
 4. git tag v$(uv version --short) && git push && git push --tags
 5. rm -rf dist && uv build
 6. uv publish   (uses UV_PUBLISH_TOKEN, a PyPI API token)
"""

__author__ = 'Patrick HOUBEN'
__credits__ = 'Walloon Agricultural Research Centre'
