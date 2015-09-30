"""
Tests that data is retained after an import/export or export/import cycle.
"""

from __future__ import unicode_literals
from __future__ import print_function

from lxml import etree
import os
from shutil import rmtree
from subprocess import check_call
from tempfile import mkdtemp
from unittest import TestCase

from xbundle import XBundle
from tests.util import clean_xml, file_from_string


class TestImportExport(TestCase):
    """
    Test that data is retained after an import/export or export/import cycle.
    """
    def test_export_import(self):
        """
        Test export then import.
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

            self.assertEqual(clean_xml(xbin), clean_xml(xbreloaded))
        finally:
            rmtree(tdir)

    def test_import_export(self):  # pylint: disable=no-self-use
        """
        Test import then export.
        """

        bundle = XBundle()
        bundle.import_from_directory(os.path.join("input_testdata", "mitx.01"))

        tdir = mkdtemp()
        try:
            bundle.export_to_directory(tdir)

            check_call([
                "diff", "-r",
                os.path.join("input_testdata", "mitx.01.exported"),
                os.path.join(tdir, "mitx.01"),
            ])
        finally:
            rmtree(tdir)

    def test_import_url_name(self):
        """
        Test that we import url_name as url_name_orig.
        """
        bundle = XBundle(keep_urls=True, keep_studio_urls=True)
        bundle.import_from_directory(os.path.join('input_testdata', 'mitx.01'))

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
        self.assertEqual(clean_xml(expected), clean_xml(bundle_string))

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
        self.assertEqual(clean_xml(expected), clean_xml(bundle_string))

    def test_save(self):
        """
        Test save method.
        """

        input_xml = "<xbundle><metadata /><course /></xbundle>"
        bundle = XBundle()
        bundle.load(file_from_string(input_xml))
        self.assertEqual(clean_xml(str(bundle)), clean_xml(input_xml))

        curdir = os.getcwd()
        tempdir = mkdtemp()
        try:
            os.chdir(tempdir)
            bundle.save()

            with open(os.path.join(tempdir, "xbundle.xml")) as f:
                self.assertEqual(clean_xml(f.read()), clean_xml(input_xml))

            bundle.save(filename="other.xml")
            with open(os.path.join(tempdir, "other.xml")) as f:
                self.assertEqual(clean_xml(f.read()), clean_xml(input_xml))

            handle_path = os.path.join(tempdir, "third.xml")
            with open(handle_path, "w") as f:
                bundle.save(file_handle=f)
            with open(handle_path) as f:
                self.assertEqual(clean_xml(f.read()), clean_xml(input_xml))
        finally:
            os.chdir(curdir)
            rmtree(tempdir)

    def test_export_and_keep_urls(self):
        """
        Test the changes to url_name after export_to_directory and import.
        """
        # Note url_name_orig in chapter.
        input_xml = """<xbundle>
  <metadata>
    <policies semester="2013_Spring">
      <gradingpolicy>y:2</gradingpolicy>
      <policy>x:1</policy>
    </policies>
    <about>
      <file filename="overview.html">hello overview</file>
    </about>
  </metadata>
  <course semester="2013_Spring" org="MITx">
    <chapter display_name="Intro" url_name_orig="Intro_chapter">
      <sequential display_name="Overview">
        <html url_name="Overview_text_html">
        hello world
        </html>
      </sequential>
      <!-- a comment -->
    </chapter>
  </course>
</xbundle>"""
        bundle = XBundle(keep_urls=True, force_studio_format=True)
        bundle.load(file_from_string(input_xml))

        # str(bundle) doesn't change input xml, but export_to_directory will.
        self.assertEqual(clean_xml(input_xml), clean_xml(str(bundle)))

        old_current_dir = os.getcwd()
        tempdir = mkdtemp()
        try:
            os.chdir(tempdir)
            bundle.export_to_directory()

            bundle2 = XBundle(keep_urls=True, force_studio_format=True)
            bundle2.import_from_directory()

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
  <course semester="2013_Spring" org="MITx" course=""
    url_name_orig="2013_Spring">
    <chapter display_name="Intro" url_name_orig="Intro_chapter">
      <sequential display_name="Overview"
        url_name_orig="Overview_sequential">
        <vertical url_name_orig="Overview_vertical"
            display_name="Overview_vertical">
          <html url_name_orig="Overview_text_html"
            display_name="Overview_text_html">
        hello world
        </html>
        </vertical>
      </sequential>
      <!-- a comment -->
    </chapter>
  </course>
</xbundle>"""

            self.assertEqual(clean_xml(expected), clean_xml(str(bundle2)))
        finally:
            os.chdir(old_current_dir)
            rmtree(tempdir)

    def test_xml_header(self):
        """
        Test removal of xml attribute.
        """
        input_xml = """<?xml version="1.0"?>
<xbundle>
  <metadata />
  <course />
</xbundle>
"""

        bundle = XBundle()
        bundle.load(file_from_string(input_xml))
        self.assertEqual(clean_xml(input_xml), clean_xml(str(bundle)))

    def test_import_skip_hidden(self):
        """
        Test skip_hidden flag.
        """
        bundle = XBundle(skip_hidden=True)
        path = os.path.join('input_testdata', 'mitx.01')
        bundle.import_from_directory(path)

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
  <course semester="2013_Spring" course="mitx.01" org="MITx">
    <chapter display_name="Intro">
      <sequential display_name="Overview">
        <html display_name="Overview text">\n        hello world\n      </html>
      </sequential>
      <!-- a comment -->
    </chapter>
  </course>
</xbundle>
"""

        self.assertEqual(clean_xml(str(bundle)), clean_xml(expected))

    def test_import_large(self):
        """
        Test import of a course slightly larger than mitx.01.
        """
        bundle = XBundle()
        path = os.path.join('input_testdata', 'content-devops-0001')
        bundle.import_from_directory(path)

        expected_path = os.path.join(
            'input_testdata', 'content-devops-0001.out.xml')
        with open(expected_path) as f:
            self.assertEqual(clean_xml(f.read()), clean_xml(str(bundle)))

        tempdir = mkdtemp()
        try:
            bundle.export_to_directory(tempdir, xml_only=True, newfmt=True)

            for root, _, files in os.walk(os.path.join(tempdir, "0.001")):
                for filename in files:
                    abs_path = os.path.join(root, filename)
                    # We set xml_only=True so there shouldn't be anything else.
                    self.assertTrue(abs_path.endswith(".xml"))
        finally:
            rmtree(tempdir)
