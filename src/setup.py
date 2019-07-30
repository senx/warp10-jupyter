#
#   Copyright 2018  SenX S.A.S.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

class Warp10_Downloader(install):
      """Downloads Warp10 archive for local warpscript execution"""

      def run(self):
            from warpscript.warp10_version import get_Warp10_jar_path
            get_Warp10_jar_path()
            install.run(self)

class Warp10_Downloader_dev(develop):
      """Downloads Warp10 archive for local warpscript execution"""

      def run(self):
            from warpscript.warp10_version import get_Warp10_jar_path
            get_Warp10_jar_path()
            develop.run(self)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='warp10-jupyter',
      version='0.7',
      description='Functions and Jupyter extension for executing WarpScript code',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/senx/warp10-jupyter',
      author='Jean-Charles Vialatte',
      author_email='jean-charles.vialatte@senx.io',
      license='Apache 2.0',
      packages=['warpscript'],
      install_requires=['py4j', 'jupyter', 'requests', 'future'],
      zip_safe=False,
      include_package_data=True,
      cmdclass={
            'develop': Warp10_Downloader_dev,
            'install': Warp10_Downloader
            })
