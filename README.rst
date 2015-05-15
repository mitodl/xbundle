xbundle
=======

``xbundle`` converts back and forth between OLX and "xbundle" style XML
formats. The xbundle format is a single XML file.

The OLX format is defined in `this
documentation <http://edx-open-learning-xml.readthedocs.org/en/latest/>`__.

Installation
------------

``python setup.py install``

This will install ``xbundle`` and the ``xbundle_convert`` command-line
tool.

--------------

Using xbundle in your code
--------------------------

To convert from xbundle to OLX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

        from xbundle import XBundle

        bundle = XBundle()
        # get input_path and output_path from user input 
        bundle.load(input_path)
        bundle.export_to_directory(output_path)

To convert from OLX to xbundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

        from xbundle import XBundle

        bundle = XBundle()
        # get input_path and output_path from user input 
        bundle.import_from_directory(input_path)
        bundle.save(output_path)

--------------

Using the command-line tool
---------------------------

``xbundle_convert convert /path/to/course /path/to/output.xml``

or

``xbundle_convert convert /path/to/output.xml /path/to/course``

--------------

Run tests
---------

``xbundle_convert test``
