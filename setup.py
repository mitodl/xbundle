"""
setup.py for PyPi
"""
from setuptools import setup

setup(
    name='xbundle',
    version="0.1.1",
    packages=['xbundle'],
    scripts=['bin/xbundle_convert'],
    author='Isaac Chuang, Shawn Milochik',
    author_email='ichuang@mit.edu, milochik@mit.edu',
    description='Converts edX courses between OLX and single-XML formats.',
    url='https://github.com/mitodl/xbundle',
    install_requires=['lxml', 'BeautifulSoup', 'docopt'],
)
