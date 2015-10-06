"""
Misc tests for helper functions.
"""

from __future__ import unicode_literals
from __future__ import print_function

import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from xbundle import mkdir


class TestXBundle(TestCase):
    """
    Misc tests for helper functions.
    """

    def test_mkdir(self):
        """
        Test functionality of mkdir.
        """
        tempdir = mkdtemp()
        try:
            new_dir = os.path.join(tempdir, "a", "b", "c", "d", "e'")
            mkdir(new_dir)
            self.assertTrue(os.path.isdir(new_dir))
            mkdir(new_dir)
            self.assertTrue(os.path.isdir(new_dir))
        finally:
            rmtree(tempdir)
