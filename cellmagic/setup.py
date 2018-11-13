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

from setuptools import setup

setup(name='warp10-jupyter',
      version='0.3',
      description='Jupyter extension that contains a cell magic to execute WarpScript code',
      #url='http://gitlab.com/jecv/warp10-jupyter',
      author='Jean-Charles Vialatte',
      author_email='jean-charles.vialatte@senx.io',
      license='Apache 2.0',
      packages=['warpscript'],
      install_requires=['py4j', 'jupyter'],
      zip_safe=False)