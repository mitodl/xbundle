"""
Test input data.
"""

from __future__ import unicode_literals


EMPTY_COURSE = """<xbundle>
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


NO_COURSE = """
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


URL_NAME_ORIG_IN_CHAPTER1 = """<xbundle>
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


URL_NAME_ORIG_IN_CHAPTER2 = """<xbundle>
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


COURSE = """
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


POLICIES = """
<policies semester='2013_Spring'>
  <gradingpolicy>y:2</gradingpolicy>
  <policy>x:1</policy>
</policies>
"""


EMPTY_XBUNDLE = """<?xml version="1.0"?>
<xbundle>
  <metadata />
  <course />
</xbundle>
"""
