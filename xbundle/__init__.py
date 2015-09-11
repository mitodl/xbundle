#!/usr/bin/env python
"""
XBundle class

an xbundle file is an XML format file with element <xbundle>, which
includes the following sub-elements:

<metadata>
  <policies semester=...>: <policy> and <gradingpolicy>
                           each contain the JSON for the corresponding file
  <about>: <file filename=...> </about>
</metadata>
<course semester="...">: course XML </course>

The XBundle class represents an xbundle file; it can read and write
the file, and it can import and export to standard edX (unbundled) format.
"""

from __future__ import unicode_literals

import os
import re
import logging
from glob import glob
import subprocess
from os.path import join, exists, basename

from lxml import etree
import unicodedata
log = logging.getLogger()  # pylint: disable=invalid-name
logging.basicConfig()
log.setLevel(logging.DEBUG)

POLICY_TAG_MAP = {'policy': 'policy', 'gradingpolicy': 'grading_policy'}

# star-args aren't offensive, and pylint has a lot of trouble with
# members in the lxml package.
# pylint: disable=no-member,star-args

DESCRIPTOR_TAGS = set([
    'course', 'chapter', 'sequential', 'vertical', 'html', 'problem', 'video',
    'conditional', 'combinedopenended', 'videosequence', 'problemset',
    'wrapper', 'poll_question', 'randomize', 'proctor', 'discussion',
    'staffgrading',
])

class XBundle(object):
    """
    An XBundle is defined by two elements: course and metadata.
    metadata includes policies and about.
    """
    def __init__(
            self, keep_urls=False, force_studio_format=False,
            skip_hidden=False, keep_studio_urls=False,
            no_overwrite=None, preserve_url_name=False,
        ):
        """
        if keep_urls=True then the original url_name attributes are kept upon
                     import and export,
        if nonrandom (ie non-Studio).

        if keep_studio_urls=True and keep_urls=True, then keep random urls.

        if preserve_url_name=True, store urls as url_name instead of url_name_orig

        no_overwrite: optional list of xml tags for which files should not
                      be overwritten (eg course)
        """
        self.course = etree.Element('course')
        self.metadata = etree.Element('metadata')
        self.urlnames = []
        self.xml = None  # only used if XML xbundle file was read in
        self.keep_urls = keep_urls
        # sequential must be followed by vertical in export
        self.force_studio_format = force_studio_format
        self.skip_hidden = skip_hidden
        self.keep_studio_urls = keep_studio_urls
        self.preserve_url_name = preserve_url_name
        self.no_overwrite = no_overwrite or []
        self.path = ""
        self.semester = ""
        self.export = None

    def set_course(self, xml):
        """
        Set self.course from the XML passed in.
        """
        if not xml.tag == 'course':
            log.error('set_course should be called with a <course> element')
            return
        if not 'org' in xml.attrib:
            xml.set('org', "MITx")
        semester = xml.get('url_name', xml.get('semester', ''))
        if semester == "":
            log.error("No semester found.")
        if not 'semester' in xml.attrib:
            xml.set('semester', semester)
        self.semester = semester
        self.course = xml
        # Fill up self.urlnames with existing ones if keep_urls.
        if self.keep_urls:
            def walk(xml):
                """
                Recursively walk XML and gather url names.
                """
                url_name = xml.get('url_name', '')
                if url_name:
                    self.urlnames.append(url_name)
                if xml.tag in DESCRIPTOR_TAGS:
                    for child in xml:
                        walk(child)
            walk(xml)

    def add_policies(self, policies):
        """add a policies XML subtree to the metadata"""
        self.metadata.append(policies)

    def add_about_file(self, filename, filedata):
        """
        Add a file to the about element.
        """
        about = self.metadata.find('about')
        if about is None:
            about = etree.SubElement(self.metadata, 'about')
        abfile = etree.SubElement(about, 'file')
        abfile.set('filename', filename)
        abfile.text = filedata
        # Unicode characters in the "about" HTML file were causing
        # the lxml package to break.
        if not isinstance(filedata, str):
            abfile.text = filedata.decode('utf-8')
        else:
            abfile.text = filedata

    def load(self, filename):
        """
        Load from xbundle.xml file
        """
        self.xml = etree.parse(filename).getroot()
        self.course = self.xml.find('course')
        self.metadata = self.xml.find('metadata')
        log.debug("course id = %s", self.course.get('course', ''))

    def save(self, filename='xbundle.xml', file_handle=None):
        """
        Save to xbundle.xml file.
        """
        if file_handle is None:
            with open(filename, 'w') as output:
                output.write(str(self))
            return
        file_handle.write(str(self))

    def __str__(self):
        xml = etree.Element('xbundle')
        self.xml = xml
        xml.append(self.metadata)
        xml.append(self.course)
        return pp_xml(xml)

    def import_from_directory(self, path='./'):
        """
        Create xbundle from edX XML directory.
        Using this is a great way to sanitize directory structure
        and also normalize url_name filenames (and make them
        meaningfully human readable).
        """
        self.metadata = etree.Element('metadata')
        self.import_metadata_from_directory(path)
        self.import_course_from_directory(path)

    def import_metadata_from_directory(self, path):
        """
        Load policies.
        """
        for pdir in glob(join(path, 'policies/*')):
            policies = etree.Element('policies')
            policies.set('semester', basename(pdir))
            policy_files = set(["policy.json", "grading_policy.json"])
            for filename in glob(join(pdir, '*.json')):
                if basename(filename) not in policy_files:
                    continue
                elem = etree.SubElement(policies, basename(
                    filename).replace('_', '').replace('.json', ''))
                with open(filename, "rb") as data:
                    elem.text = data.read().decode('utf-8')
            self.add_policies(policies)

        # Load "about" files.
        for afn in glob(join(path, 'about/*')):
            try:
                with open(afn, "rb") as data:
                    self.add_about_file(
                        basename(afn), data.read().decode("utf-8"))
            except ValueError as err:
                log.warning("Failed to add file %s, error=%s", afn, err)

    def import_course_from_directory(self, path):
        """
        Load course tree, removing intermediate descriptors with url_name.
        """
        elem = etree.parse(join(path, 'course.xml')).getroot()
        semester = elem.get(
            'url_name',
            '')		# the url_name of <course> is special - the semester
        cxml = self.import_xml_removing_descriptor(path, elem)
        cxml.set('semester', semester)
        self.course = cxml
        self.fix_old_course_section()
        self.fix_old_descriptor_name(self.course)

    def fix_old_descriptor_name(self, xml):
        """
        Turn name -> display_name on descriptor tags.
        """
        if xml.tag in DESCRIPTOR_TAGS:
            if 'name' in xml.attrib and not xml.get('display_name', ''):
                xml.set('display_name', xml.get('name'))
                xml.attrib.pop('name')
            for child in xml:
                self.fix_old_descriptor_name(child)

    def fix_old_course_section(self):
        """
        Remove <section>
        """
        for sect in self.course.findall('.//section'):
            for seq in sect.findall('.//sequential'):
                for k in seq:
                    seq.addprevious(k)
                sect.remove(seq)		# remove sequential from inside section
            sect.tag = 'sequential'

    def is_not_random_urlname(self, url_name):
        """
        Check whether a url_name *looks* random.
        """
        if self.keep_studio_urls:		# keep url even if random looking
            return True
        # random urlname eg: 55bc076ad06e4ede9d0561948c03be2f
        nrand = len('55bc076ad06e4ede9d0561948c03be2f')
        if not len(url_name) == nrand:
            return True
        ndigits = len([z for z in url_name if z.isdigit()])
        if ndigits < 6:
            return True
        return False  # ie seems to be random

    def update_metadata_from_policy(self, xml):
        """
        Update metadata for this element from policy, if exists.
        """
        policy = getattr(self, 'policy')
        pkey = '{0}/{1}'.format(
            xml.tag,
            xml.get('url_name', xml.get('url_name_orig', '<no_url_name>')),
        )
        if policy and pkey in policy:
            for (key, val) in policy[pkey].iteritems():
                if xml.get(key, None) is None:
                    xml.set(key, str(val))

    def import_xml_removing_descriptor(self, path, xml):
        """
        Load XML file, recursively following and removing intermediate
        descriptors with url_name.

        If element is a DescriptorTag element, and display_name is missing,
        then use its url_name, if that is available.
        """
        url_name = xml.get('url_name', '')
        if xml.tag in DESCRIPTOR_TAGS and 'url_name' in xml.attrib and url_name:
            # XML stores path separator as a colon.
            log.debug("xml.tag: " + xml.tag + " is in DESCRIPTOR_TAGS and url_name (" + url_name + ") is in xml.attrib;")
            unfn = url_name.replace(':', '/')
            filename = join(path, xml.tag, (unfn + '.xml'))
            if exists(filename):
                try:
                    log.debug("and filename " + filename + " exists; parsing.")
                    dxml = etree.parse(filename).getroot()
                    log.debug("dxml is:  " + str(dxml))
                except Exception as err:
                    log.error("Error parsing xml for %s", filename)
                    raise
                try:
                    dxml.attrib.update(xml.attrib)
                except Exception as err:
                    msg = (
                        "[xbundle] error updating attribute, dxml=%s\nxml=%s"
                        "dxml.attrib=%s xml.attrib=%s (likely your version "
                        "of lxml is too old (need version >= 3)"
                    )
                    log.error(
                        msg, etree.tostring(dxml), etree.tostring(xml),
                        dxml.attrib, xml.attrib,
                    )
                    raise
                dxml.attrib.pop('url_name')

                # Keep url_name as url_name_orig.
                if self.keep_urls and self.is_not_random_urlname(url_name):
                    if self.preserve_url_name:
                        dxml.set('url_name', url_name)
                    else:
                        dxml.set('url_name_orig', url_name)

                if dxml.tag in DESCRIPTOR_TAGS and dxml.get('display_name') is None:
                    # Special case: don't add display_name to course.
                    if dxml.tag != 'course':
                        dxml.set('display_name', url_name)

                if self.skip_hidden:
                    self.update_metadata_from_policy(dxml)
                    if xml.get('hide_from_toc', '') == 'true':
                        log.debug(
                            "[xbundle] Skipping %s (%s), it has hide_from_toc=true",
                            xml.tag, xml.get('display_name', '<noname>'))
                    else:
                        xml = dxml
                else:
                    xml = dxml

        filename = xml.get('filename', '')
        # Special for <html filename="..." display_name="..."/>.
        if xml.tag in ['html', 'problem'] and filename:
            if xml.tag == 'html':
                if not filename.endswith('.html'):
                    filename += '.html'
                options = {
                    "parser": etree.HTMLParser(
                        compact=False,
                        recover=True,
                        remove_blank_text=True
                    )
                }
            elif xml.tag == 'problem':
                if not filename.endswith('.xml'):
                    filename += '.xml'
                options = {}

            if not exists(join(path, xml.tag, filename)):
                if '-' in filename:
                    filename = '{0}/{1}'.format(
                        filename.split('-', 1)[0], filename)
            try:
                dxml = etree.parse(
                    join(path, xml.tag, filename), **options).getroot()
            except ValueError as err:
                msg = "Error!  Can't load and parse HTML file %s, error: %s"
                log.error(msg, join(path, xml.tag, filename), err)
                dxml = None
            if dxml is not None:
                if 'xmlns' in dxml.attrib:
                    dxml.attrib.pop('xmlns')
                dxml.attrib.update(xml.attrib)
                dxml.attrib.pop('filename')
                if dxml.tag in DESCRIPTOR_TAGS and dxml.get(
                        'display_name') is None:
                    dxml.set('display_name', url_name)
                xml = dxml

        if self.skip_hidden:
            self.update_metadata_from_policy(xml)
            if xml.get('hide_from_toc', '') == 'true':
                log.debug(
                    "[xbundle] Skipping %s (%s), it has hide_from_toc=true",
                    xml.tag, xml.get('display_name', '<noname>'))
                return xml

        for child in xml:
            # Calls self recursively.
            dchild = self.import_xml_removing_descriptor(path, child)
            if not dchild == child:
                child.addprevious(dchild)  # replace descriptor with contents
                xml.remove(child)
        return xml

    def export_to_directory(self, exdir='./', xml_only=False, newfmt=True):
        """
        Export xbundle to edX xml directory
        First insert all the intermediate descriptors needed.
        Do about and XML separately.
        """
        coursex = etree.Element('course')
        semester = self.course.get('semester', '')
        semester = semester.replace(' ', '_')
        self.course.set('semester', semester)  # replace attribute just in case
        coursex.set('url_name', semester)
        coursex.set('org', self.course.get('org', ''))
        if newfmt:
            coursex.set('course', self.course.get(
                'course', self.course.get('number', '')))
        else:
            coursex.set(
                'number',
                self.course.get(
                    'number',
                    ''))  # backwards compatibility

        self.export = self.make_descriptor(self.course, semester)
        self.export.append(self.course)
        self.add_descriptors(self.course)

        self.path = mkdir(join(exdir, self.course.get('course', '')))
        if not xml_only:
            self.export_meta_to_directory()
        self.export_xml_to_directory(self.export[0], dowrite=True)

        # Write out top-level course.xml.
        self.write_xml_file(join(self.path, 'course.xml'), coursex)

    def export_meta_to_directory(self):
        """
        Write out metadata (about and policy) to directory.
        """
        pdir = mkdir(join(self.path, 'policies'))
        for pxml in self.metadata.findall('policies'):
            semester = pxml.get('semester')
            path = mkdir(join(pdir, semester))
            for k in pxml:
                filename = POLICY_TAG_MAP.get(k.tag, k.tag) + '.json'
                # Write out content to policy directory file.
                with open(join(path, filename), 'wb') as output:
                    output.write(k.text.encode('utf-8'))

        adir = mkdir(join(self.path, 'about'))
        for fxml in self.metadata.findall('about/file'):
            filename = fxml.get('filename')
            try:
                # Moved "if" statement after the "open" statement, so we
                # no longer create zero-byte files here.
                if fxml.text not in (None, ""):
                    try:
                        to_write = fxml.text.encode("utf-8")
                    except UnicodeEncodeError:
                        to_write = fxml.text
                    with open(join(adir, filename), 'wb') as output:
                        output.write(to_write)
            except IOError as err:
                log.error(
                    'failed to write about file %s, error %s',
                    join(adir, filename), err
                )

    def write_xml_file(self, filename, xml, force_overwrite=False):
        """
        Write an XML file to disk.
        """
        if (not force_overwrite) and (
                xml.tag in self.no_overwrite) and exists(filename):
            log.debug("Not overwriting %s for %s", filename, xml)
            filename = filename + '.new'
        with open(filename, 'w') as output:
            output.write(pp_xml(xml))

    def export_xml_to_directory(self, elem, dowrite=False):
        """
        Do this recursively.  If an element is a descriptor,
        then put that in its own subdirectory.
        """
        def write_xml(element):
            """
            Write XML file from an XML element.
            """
            url_name = element.get('url_name')
            if url_name is None:
                log.error("missing url_name: %s", element)
            elem.attrib.pop('url_name')
            if 'url_name_orig' in elem.attrib and self.keep_urls:
                elem.attrib.pop('url_name_orig')
            edir = mkdir(join(self.path, element.tag))
            self.write_xml_file(join(edir, url_name + '.xml'), element)
            return url_name

        if elem.tag == 'descriptor':
            # Recurse on children, depth first.
            self.export_xml_to_directory(elem[0], dowrite=True)
            # Change descriptor to point to new elem.
            elem.tag = elem.get('tag')
            elem.set('url_name', elem.get('url_name'))
            elem.attrib.pop('tag')

        else:
            # If any descriptors in children.
            if elem.findall('.//descriptor'):
                for child in elem:
                    # Recurse on children (don't necessarily write).
                    self.export_xml_to_directory(child)
            if dowrite:
                # Write to file and remove from parent.
                write_xml(elem)
                elem.getparent().remove(elem)

    def make_urlname(self, xml, parent=''):
        """
        Get a display_name from the XML, using parent's
        attributes if necessary. Also, replace some characters which
        would be invalid in a display_name.
        """
        name = xml.get('display_name', '')
        display_name = name
        if not display_name:
            xmlp = xml.getparent()
            # If no display_name, try to use parent's.
            display_name = xmlp.get('display_name', '')
            if not display_name:
                display_name = xmlp.tag
        display_name += " " + xml.tag
        display_name = display_name.encode('ascii', 'xmlcharrefreplace')
        replacements = {
            '"\':<>?|![]': '',
            ',/().;=+ ': '_',
            '/': '__',
            '&': 'and',
        }

        for key, val in replacements.items():
            for char in key:
                char_bytes = unicodedata.normalize('NFKD', char).encode('ascii', 'ignore')
                val_bytes = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore')
                display_name = display_name.replace(char_bytes, val_bytes)
                
        if name and display_name in self.urlnames and parent:
            display_name = "{0}_{1}".format(display_name, parent)
        try:
            # Sometimes it's bytes, sometimes a string...
            display_name = display_name.decode("utf-8")
        except AttributeError:
            pass
        while display_name in self.urlnames:
            key = re.match('(.+?)([0-9]*)$', display_name)
            display_name, idx = key.groups()
            idx = int(idx or 0)
            display_name += str(idx + 1)
        self.urlnames.append(display_name)
        return display_name

    def make_descriptor(self, xml, url_name='', parent=''):
        """
        Construct and return a descriptor element for the given element
        at the head of xml.

        Use url_name for the descriptor, if given.
        """
        descriptor = etree.Element('descriptor')
        descriptor.set('tag', xml.tag)
        uno = xml.get('url_name_orig', '')
        if self.keep_urls and not url_name and uno and self.is_not_random_urlname(
                uno):
            url_name = uno
        if not url_name:
            url_name = self.make_urlname(xml, parent=parent)
        descriptor.set('url_name', url_name)
        xml.set('url_name', url_name)
        return descriptor

    def add_descriptors(self, xml, parent=''):
        """
        Recursively walk through self.course and add descriptors
        A descriptor is an intermediate tag, which points to content
        via a url_name.  These are used by edX to simplify loading
        of course content.
        """
        for elem in xml:
            if self.force_studio_format:
                # studio needs seq -> vert -> other
                if xml.tag == 'sequential' and not elem.tag == 'vertical':
                    # Move child into vertical.
                    vert = etree.Element('vertical')
                    elem.addprevious(vert)
                    vert.set('url_name', self.make_urlname(vert))
                    vert.append(elem)
                    # Continue processing on the vertical.
                    elem = vert
            if elem.tag in DESCRIPTOR_TAGS:
                url_name = elem.get('url_name', '')
                desc = self.make_descriptor(elem, url_name=url_name, parent=parent)
                elem.addprevious(desc)
                # Move descriptor to become new parent of elem.
                desc.append(elem)
                # Recursive call.
                self.add_descriptors(elem, desc.get('url_name', ''))

def mkdir(path):
    """
    Make a directory only if it's missing.
    """
    if not exists(path):
        os.makedirs(path)
    return path

def pp_xml(xml):
    """
    Pretty-print XML.
    """
    try:
        proc = subprocess.Popen(
            ['xmllint', '--format', '-'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        proc.stdin.write(etree.tostring(xml))
        proc.stdin.close()
        xml = proc.stdout.read()
    except subprocess.CalledProcessError as ex:
        log.warning("xmllint not found on system: %s", ex)
        xml = etree.tostring(xml, pretty_print=True)

    if xml.startswith(b'<?xml '):
        xml = xml.decode('utf-8').split('\n', 1)[1]
    return xml


def run_tests():  # pragma: no cover
    """
    Run unit tests.
    """
    import unittest

    class TestXBundle(unittest.TestCase):
        """
        xbundle tests
        """
        # pylint: disable=too-few-public-methods
        def test_roundtrip(self):
            """
            Test import/export cycle.
            """
            print("Testing XBundle round trip import -> export")
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

            tdir = 'testdata'
            if not exists(tdir):
                os.mkdir(tdir)
            bundle.export_to_directory(tdir)

            # Test round- trip.
            xb2 = XBundle()
            xb2.import_from_directory(tdir + '/mitx.01')

            xbreloaded = str(xb2)

            if not xbin == xbreloaded:
                print("xbin")
                print(xbin)
                print("xbreloaded")
                print(xbreloaded)

            self.assertEqual(xbin, xbreloaded)

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
  <course semester="2013_Spring" course="mitx.01" org="MITx" url_name_orig="2013_Spring">
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
            self.assertEqual(expected, bundle_string)

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
  <course semester="2013_Spring" course="mitx.01" org="MITx" url_name="2013_Spring">
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
            self.assertEqual(expected, bundle_string)
            
    suite = unittest.makeSuite(TestXBundle)
    ttr = unittest.TextTestRunner()
    ttr.run(suite)
