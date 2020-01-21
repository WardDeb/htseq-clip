
import sys
import os
from codecs import open
from setuptools import setup, find_packages

if sys.version_info < (3, 5):
    print ("At least Python 3.5 is required. Please install Python 3.5.")
    exit(1)

try:
	from setuptools import setup
except ImportError as e:
    sys.stderr.write("Could not import setuptools. Please install setuptools and try again to install htseq-clip. \n Error: %s" % e)
    sys.exit(1)
	
try:
	import numpy
except ImportError as e:
    sys.stderr.write("Could not import numpy. Please install it with pip install numpy and then try again to install htseq-clip. \n Exception: %s" % e)
    sys.exit(1)

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='htseq-clip',
    version='0.2.0b',
    description='htseq-clip: a toolset for the analysis of e/iCLIP datasets',
	long_description=long_description,
    url='https://bitbucket.org/htseq-clip/htseq-clip',
    author='Marko Fritz, Thomas Schwarzl',
    author_email='marko.fritz@embl.de, schwarzl@embl.de',
	zip_safe=False,
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
	install_requires=['HTSeq', 'pandas', 'pysam', 'biopython'],
    packages=['clip','tests'],
    test_suite = 'tests',
	entry_points = {
        'console_scripts': ['htseq-clip=clip.command_line:main'],
    }
)
