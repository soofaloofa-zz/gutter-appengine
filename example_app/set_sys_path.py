import os
import sys

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def set_sys_path():
    # Add lib as primary libraries directory, with fallback to lib/dist
    # and optionally to lib/dist.zip, loaded using zipimport.
    sys.path[0:0] = [
        os.path.join(CURRENT_PATH, 'lib'),
    ]
