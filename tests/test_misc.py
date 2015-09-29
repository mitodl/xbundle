"""
Misc tests for helper functions.
"""

from __future__ import unicode_literals
from __future__ import print_function

import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from xbundle import exists, mkdir


class TestXBundle(TestCase):
    """
    Misc tests for helper functions.
    """

    def test_exists(self):
        """
        Test functionality of exists.
        """
        tempdir = mkdtemp()
        try:
            # Test against directory
            self.assertTrue(exists(tempdir))
            self.assertFalse(exists(os.path.join(tempdir, "missing")))

            # Test against file
            file_path = os.path.join(tempdir, "file")
            self.assertFalse(exists(file_path))
            with open(os.path.join(tempdir, "file"), "wb") as f:
                f.write(b"")
            self.assertTrue(exists(file_path))

            # Test against symlink (the reason we're
            # not just using os.path.exists).
            sym_path = os.path.join(tempdir, "sym")
            os.symlink(file_path, sym_path)
            self.assertTrue(exists(sym_path))

            # Invalid symlink
            sym_path2 = os.path.join(tempdir, "sym2")
            os.symlink(
                os.path.join(tempdir, "missing"), sym_path2)
            self.assertFalse(exists(sym_path2))
        finally:
            rmtree(tempdir)

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
