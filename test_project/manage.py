#!/usr/bin/env python
try:
    import pundle
    pundle.activate()
except:
    pass

from django.core.management import execute_from_command_line
import os, sys
try:
    import settings  # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write(
        """Error: Can't find the file 'settings.py' in the directory containing
%r. It appears you've customized things.\n
You'll have to run django-admin.py, passing it your settings module.
(If the file settings.py does indeed exist, it's causing an ImportError.)\n"""
        % __file__)
    sys.exit(1)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    execute_from_command_line(sys.argv)

    # fix known PyPy bug (see https://bugs.pypy.org/issue1116)
    import gc
    gc.collect()
    gc.collect()
