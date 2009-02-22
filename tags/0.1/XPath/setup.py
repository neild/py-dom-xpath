import glob
import os
import string
import sys

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.test import test as _test

# Include yapps2 from the local build directory.
sys.path.insert(0, 'yapps2')
import yapps2

class test(_test):
    # Specialization of the setuptools test command, which adds the build_py
    # step as a prerequisite.

    def run(self):
        self.run_command('build_py')
        _test.run(self)

class build_py(_build_py):
    # Specialization of the setuptools build_py command, which will use
    # yapps2 to compile .g parser definitions into modules.

    def initialize_options(self):
        _build_py.initialize_options(self)
        self.yapps = {}

    def build_module(self, module, source, package):
        if source in self.yapps:
            yapps2.generate(self.yapps[source], source)
        return _build_py.build_module(self, module, source, package)

    def find_package_modules(self, package, package_dir):
        modules = _build_py.find_package_modules(self, package, package_dir)

        yapps_files = glob.glob(os.path.join(package_dir, '*.g'))
        for f in yapps_files:
            py_f = os.path.splitext(f)[0] + '.py'
            self.yapps[py_f] = f
            module = os.path.splitext(os.path.basename(f))[0]
            mdef = (package, module, py_f)
            if mdef not in modules:
                modules.append(mdef)

        return modules

setup(name="py-dom-xpath",
      version="0.1",
      description="XPath for DOM trees",
      long_description="""\
py-dom-xpath is a pure Python implementation of XPath 1.0. It
supports almost all XPath 1.0, with the main exception being the
namespace axis. It operates on DOM 2.0 nodes, and works well with
xml.dom.minidom.

py-dom-xpath requires Python 2.5 or greater.""",
      author='Damien Neil',
      author_email='damien.neil@gmail.com',
      url='http://code.google.com/p/py-dom-xpath/',
      download_url='http://py-dom-xpath.googlecode.com/files/py-dom-xpath-0.1.tar.gz',
      packages=['xpath'],
      cmdclass={
          'build_py':build_py,
          'test':test,
      },
      test_suite='tests',
      )
