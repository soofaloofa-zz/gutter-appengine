"""
AppEngine Config
"""

import os
import sys

sys.path[0:0] = [
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib'),
]

import gutter_config  # noqa
