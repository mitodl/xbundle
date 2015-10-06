"""
Test expected data.
"""

from __future__ import unicode_literals


URL_NAME_ORIG = """<xbundle>
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


SET_COURSE = """<xbundle>
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


ESCAPED_UNICODE = """<xbundle>
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


MISSING_SECTION = """<xbundle>
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


SKIP_HIDDEN = """<xbundle>
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


KEEP_URLS = """<xbundle>
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


PRESERVE_URL_NAME = """<xbundle>
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


KEEP_URLS_FORCE_STUDIO_FORMAT = """<xbundle>
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
