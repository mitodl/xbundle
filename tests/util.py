"""
Helper functions shared between tests.
"""

from __future__ import unicode_literals
from __future__ import print_function

from lxml import etree
from six import StringIO


def clean_xml(xml_str):
    """
    Remove whitespace from XML.
    """
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.tostring(
        etree.XML(xml_str, parser=parser))


def file_from_string(xml_str):
    """
    Create a fake file object with string's contents.
    """
    stringio = StringIO()
    stringio.write(xml_str)
    stringio.seek(0)
    return stringio
