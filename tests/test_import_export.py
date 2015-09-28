"""
Tests that data is retained after an import/export or export/import cycle.
"""

from __future__ import unicode_literals
from __future__ import print_function

from lxml import etree
import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from xbundle import XBundle


class TestImportExport(TestCase):
    """
    Test that data is retained after an import/export or export/import cycle.
    """
    @staticmethod
    def format(xml_str):
        """
        Remove whitespace from XML.
        """
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.tostring(
            etree.XML(xml_str, parser=parser))

    def test_roundtrip(self):
        """
        Test import/export cycle.
        """
        bundle = XBundle()
        cxmls = """
<course semester="2013_Spring" course="mitx.01">
  <chapter display_name="Intro">
    <sequential display_name="Overview">
      <html display_name="Overview text">
        hello world
      </html>
    </sequential>
    <!-- a comment -->
  </chapter>
</course>
"""

        pxmls = """
<policies semester='2013_Spring'>
  <gradingpolicy>y:2</gradingpolicy>
  <policy>x:1</policy>
</policies>
"""

        bundle.set_course(etree.XML(cxmls))
        bundle.add_policies(etree.XML(pxmls))
        bundle.add_about_file("overview.html", "hello overview")

        xbin = str(bundle)

        tdir = mkdtemp()
        try:
            bundle.export_to_directory(tdir)

            # Test round- trip.
            xb2 = XBundle()
            xb2.import_from_directory(os.path.join(tdir, 'mitx.01'))

            xbreloaded = str(xb2)

            self.assertEqual(self.format(xbin), self.format(xbreloaded))
        finally:
            rmtree(tdir)

    def test_import_url_name(self):
        """
        Test that we import url_name as url_name_orig.
        """
        bundle = XBundle(keep_urls=True, keep_studio_urls=True)
        bundle.import_from_directory('input_testdata/mitx.01')

        bundle_string = str(bundle)

        expected = """<xbundle>
  <metadata>
    <policies semester="2013_Spring">
      <gradingpolicy>y:2</gradingpolicy>
      <policy>x:1</policy>
    </policies>
    <about>
      <file filename="overview.html">hello overview</file>
    </about>
  </metadata>
  <course semester="2013_Spring" course="mitx.01" org="MITx"
   url_name_orig="2013_Spring">
    <chapter display_name="Intro" url_name_orig="Intro_chapter">
      <sequential display_name="Overview">
        <html display_name="Overview text" url_name_orig="Overview_text_html">
        hello world
      </html>
      </sequential>
      <!-- a comment -->
    </chapter>
  </course>
</xbundle>
"""
        self.assertEqual(self.format(expected), self.format(bundle_string))

    def test_preserve_url_name(self):
        """
        Test that preserve_url_name imports as url_name and not url_name_orig.
        """
        bundle = XBundle(
            keep_urls=True, keep_studio_urls=True, preserve_url_name=True)
        bundle.import_from_directory('input_testdata/mitx.01')

        bundle_string = str(bundle)

        expected = """<xbundle>
  <metadata>
    <policies semester="2013_Spring">
      <gradingpolicy>y:2</gradingpolicy>
      <policy>x:1</policy>
    </policies>
    <about>
      <file filename="overview.html">hello overview</file>
    </about>
  </metadata>
  <course semester="2013_Spring" course="mitx.01" org="MITx"
   url_name="2013_Spring">
    <chapter display_name="Intro" url_name="Intro_chapter">
      <sequential display_name="Overview">
        <html display_name="Overview text" url_name="Overview_text_html">
        hello world
      </html>
      </sequential>
      <!-- a comment -->
    </chapter>
  </course>
</xbundle>
"""
        self.assertEqual(self.format(expected), self.format(bundle_string))
