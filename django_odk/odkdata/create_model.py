import os
import glob
import logging

from django.core.management import call_command
from xlsconv.django import xls2django
from config.settings import MEDIA_ROOT
from odk.models import XForm
from odkdata.utils import rm_digit, convert2camelcase


odkdata_dir = os.path.dirname(__file__)


LOG = logging.getLogger(__name__)



def get_last_file():
    """
    return
    xls_path: "/var/www/projectname/media/XForm/pdt9.xlsx"
    xls_name: "pdt9.xlsx"
    xls_root: "pdt"
    Not used for the moment (should check form_id inside xml)
    """
    xform_path = os.path.join(MEDIA_ROOT, 'XForm/')
    xlsx_path = f"{xform_path}*.xlsx"
    file_list = glob.glob(xlsx_path)

    xls_path = max(file_list, key=os.path.getctime)
    xls_name = xls_path.replace(xform_path, '').replace('.xlsx', '')
    xls_root = rm_digit(xls_name).replace('.xlsx', '')

    return xls_path, xls_name, xls_root


def get_xlsx_path(xform):
    """Not used"""
    if xform is None:
        xls_path, xls_name, xls_root = get_last_file()
    else:
        xls_path = xform.xls_file.path
        xls_name = xform.xls_file.name
        xls_root = rm_digit(xls_name).replace('.xlsx', '')

    LOG.warning(f"xls_path: {xls_path}, xls_root: {xls_root}")
    return xls_path, xls_name, xls_root
    

def append_init_file(pkg_name):
    """
    Check init content and add new model declaration if absent
    """
    model_name = convert2camelcase(pkg_name)
    path = os.path.join(odkdata_dir, 'models', '__init__.py')
    newline = f"from odkdata.models.{pkg_name} import {model_name}\n"

    try:
        with open(path, "r") as init_file_r:
            lines = init_file_r.readlines()
    except (IOError, OSError) as e:
        LOG.error(e)

    if newline not in lines:
        with open(path, "a+") as init_file:
            init_file.write(newline)


def model_correction(pkg_path, form_id):
    """
    Loop through model created by xlsconv.django.xls2django
    an rewrite it with 3 changes
    1. rename all old_names > new_names (ex: Pdt9 become Pdt)
    2. create UUID field instanceid
    3. add "null=True, blank=True" for srid field
    """
    old_name = convert2camelcase(form_id)
    new_name = convert2camelcase(rm_digit(form_id))

    path_old = pkg_path
    path_new = f"{odkdata_dir}/models/{rm_digit(form_id)}.py"
    sp4 = "    "
    try:
        with open(path_old, "r") as f_old, open(path_new, "w") as f_new:
            for line in f_old:
                # replace all old_name to new_name
                line = line.replace(old_name, new_name).replace(old_name.lower(), new_name.lower())
                f_new.write(line)

                if f"class {new_name}(models.Model):\n" in line:
                    f_new.write(f"{sp4}instanceid = models.UUIDField(unique=True)\n")
                if 'srid=4326,' in line:
                    f_new.write(f"{sp4}{sp4}null=True, blank=True,\n")
    except (IOError, OSError) as e:
        LOG.error(e)
        return False

    return True


def process(xform=None):
    """
    param: XForm instance
    return Boolean
    """
    if xform is None:
        LOG.warning("You must provide a XForm instance")
        return False
        
    # 1. Init vars
    xls_path = xform.xls_file.path
    pkg_name = rm_digit(xform.form_id)
    
    pkg_path = os.path.join(odkdata_dir, 'models', f"{pkg_name}_orig.py")

    # 2. xls2django
    fpointer = xls2django(xls_path)
    try:
        with open(pkg_path, "w") as fmodel:
            print(fpointer, file=fmodel)
    except (IOError, OSError) as e:
        LOG.error(e)
        return False

    # 3. Append_init
    try:
        append_init_file(pkg_name)
    except Exception as xcpt:
        LOG.error(xcpt)
        return False
    
    # 4. Model correction
    if not model_correction(pkg_path, xform.form_id):
        return False

    return True


def apply_changes2db():
    """
    function calling
    makemigrations and migrate
    Works fine but no feedback to user => Leave from now 2022-06-16
    """
    try:
        call_command('makemigrations', 'odkdata')
    except Exception as xcpt:
        LOG.error(xcpt)
        return False

    try:
        call_command('migrate')
    except Exception as xcpt:
        LOG.error(xcpt)
        return False
    return True