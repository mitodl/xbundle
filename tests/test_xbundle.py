"""
Misc tests for XBundle object.
"""

from __future__ import unicode_literals
from __future__ import print_function

import os
from lxml import etree
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from xbundle import XBundle
from tests.util import clean_xml, file_from_string


class TestXBundle(TestCase):
    """
    Misc tests for XBundle object.
    """

    def test_set_course(self):
        """
        Test functionality of set_course.
        """
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
  <course  />
</xbundle>
"""

        bundle = XBundle(keep_urls=True)
        bundle.load(file_from_string(input_xml))

        # No org or semester is specified in XML above.
        self.assertEqual(bundle.course.get("org"), None)
        self.assertEqual(bundle.course.get("semester"), None)
        self.assertEqual(bundle.semester, "")

        # Note lack of org attribute and url_name for course element.
        course_str = """
<course semester="2013_Spring" >
    <chapter display_name="Intro" url_name="Intro_chapter">
      <sequential display_name="Overview">
        <html display_name="Overview text" url_name="Overview_text_html">
        hello world
        </html>
      </sequential>
      <!-- a comment -->
    </chapter>
</course>
"""
        with self.assertRaises(Exception) as ex:
            bundle.set_course(etree.XML("<x>" + course_str + "</x>"))
        self.assertTrue(
            "set_course should be called with a <course> element"
            in ex.exception.args)

        with self.assertRaises(Exception) as ex:
            bundle.set_course(etree.XML("<course />"))
        self.assertTrue("No semester found." in ex.exception.args)

        bundle.set_course(etree.XML("<course url_name='x' />"))
        self.assertEqual(bundle.semester, "x")

        bundle.set_course(etree.XML(course_str))

        # MITx is not present in data, it is automatically set.
        self.assertEqual(bundle.course.get("org"), "MITx")
        self.assertEqual(bundle.course.get("semester"), "2013_Spring")
        self.assertEqual(bundle.semester, "2013_Spring")

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
  <course semester="2013_Spring" org="MITx">
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
        self.assertEqual(clean_xml(bundle_string), clean_xml(expected))

    def test_add_descriptors(self):
        """
        Test add_descriptors.
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
        <html display_name="Overview text" url_name="Overview_text_html">
        hello world
        </html>
      </sequential>
      <!-- a comment -->
    </chapter>
  </course>
</xbundle>"""
        bundle = XBundle(keep_urls=True)
        bundle.load(file_from_string(input_xml))

        # str(bundle) doesn't change input xml, but export_to_directory will.
        self.assertEqual(clean_xml(input_xml), clean_xml(str(bundle)))

        old_current_dir = os.getcwd()
        tempdir = mkdtemp()
        try:
            os.chdir(tempdir)
            bundle.export_to_directory()

            bundle2 = XBundle(keep_urls=True)
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
      <sequential display_name="Overview" url_name_orig="Overview_sequential">
        <html display_name="Overview text" url_name_orig="Overview_text_html">
        hello world
        </html>
      </sequential>
      <!-- a comment -->
    </chapter>
  </course>
</xbundle>"""

            self.assertEqual(clean_xml(expected), clean_xml(str(bundle2)))
        finally:
            os.chdir(old_current_dir)
            rmtree(tempdir)

    def test_is_not_random_urlname(self):
        """
        Test behavior of is_not_random_urlname.
        """
        # Randomness test used in method
        input_hash = 'z5bc076ad06e4ede9d0561948c03be2f'
        input_letters = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
        input_empty = ''

        # Since keep_studio_urls is True
        bundle_studio_urls = XBundle(keep_studio_urls=True)
        self.assertTrue(bundle_studio_urls.is_not_random_urlname(input_hash))
        self.assertTrue(
            bundle_studio_urls.is_not_random_urlname(input_letters))
        self.assertTrue(bundle_studio_urls.is_not_random_urlname(input_empty))

        bundle = XBundle()
        self.assertFalse(bundle.is_not_random_urlname(input_hash))
        self.assertTrue(bundle.is_not_random_urlname(input_letters))
        self.assertTrue(bundle.is_not_random_urlname(input_empty))

    def test_unicode_in_html(self):
        """
        Test that unicode doesn't cause problems in overview file.
        """
        bundle = XBundle()
        bundle.import_from_directory(os.path.join("input_testdata", "mitx.01"))
        bundle.add_about_file("overview.html",
                              "\u2e18 interrobang \u203d")

        expected = """<xbundle>
  <metadata>
    <policies semester="2013_Spring">
      <gradingpolicy>y:2</gradingpolicy>
      <policy>x:1</policy>
    </policies>
    <about>
      <file filename="overview.html">hello overview</file>
      <file filename="overview.html">&#x2E18; interrobang &#x203D;</file>
    </about>
  </metadata>
  <course semester="2013_Spring" course="mitx.01" org="MITx">
    <chapter display_name="Intro">
      <sequential display_name="Overview">
        <html display_name="Overview text">
        hello world
      </html>
      </sequential>
      <!-- a comment -->
    </chapter>
  </course>
</xbundle>"""
        self.assertEqual(clean_xml(str(bundle)), clean_xml(expected))

        # Reimport to start from a clean slate. This time use bytes.
        bundle = XBundle()
        bundle.import_from_directory(os.path.join("input_testdata", "mitx.01"))

        bundle.add_about_file(
            "overview.html", "\u2e18 interrobang \u203d".encode('utf-8'))
        self.assertEqual(clean_xml(str(bundle)), clean_xml(expected))

    def test_fix_old_descriptor_name(self):
        """
        Test fix_old_descriptor_name.
        """
        bundle = XBundle()
        elem = etree.XML('<sequential name="abc" />')
        bundle.fix_old_descriptor_name(elem)

        expected = '<sequential display_name="abc" />'
        self.assertEqual(clean_xml(expected), clean_xml(etree.tostring(elem)))

    def test_fix_old_course_section(self):
        """
        Test fix_old_course_section.
        """
        bundle = XBundle()
        bundle.import_from_directory(
            os.path.join("input_testdata", "sections"))

        # Section element should be removed.
        expected = """<xbundle>
  <metadata/>
  <course semester="2013_Spring" course="mitx.01" org="MITx">
    <chapter display_name="Intro">
      <sequential>
        <!-- a comment -->
      </sequential>
    </chapter>
  </course>
</xbundle>
"""
        self.assertEqual(clean_xml(expected), clean_xml(str(bundle)))
