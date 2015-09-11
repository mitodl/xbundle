"""
setup.py for PyPi
"""
from setuptools import setup

with open('README.rst') as readme_file:
    README = readme_file.read()

setup(
    name='xbundle',
    version="0.3.1",
    packages=['xbundle'],
    scripts=['bin/xbundle_convert'],
    author='MIT ODL Engineering',
    author_email='odl-engineering@mit.edu',
    description='Converts edX courses between OLX and single-XML formats.',
    url='https://github.com/mitodl/xbundle',
    install_requires=['lxml', 'docopt'],
    license='BSD',
    long_description=README,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
    ],
)
