"""
App storage to avoid multiple file creation on server like:
- sample_template.xml
- sample_template_AQXj3PD.xml
- sample_template_d2DxYEQ.xml
- sample_template_Pc45KRk.xml
"""
import os

from django.core.files.storage import FileSystemStorage
from django.core.files.utils import validate_file_name
from config.settings import MEDIA_ROOT


class OverwriteMixin(object):
    """
    Update get_available_name to remove any previously stored file (if any) before returning the
    name.
    """
    def get_available_name(self, name, max_length=None):
        # Reject '..' / absolute paths BEFORE deleting anything: Django only
        # validates the name after _save(), i.e. after we would have removed
        # (and the storage rewritten) an arbitrary file under MEDIA_ROOT.
        validate_file_name(name, allow_relative_path=True)
        self.delete(name)
        return name


class OverwriteStorage(OverwriteMixin, FileSystemStorage):
    """A file-system based storage that let overwrite files with the same name."""


overwrite_storage = OverwriteStorage()
