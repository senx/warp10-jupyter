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
import tarfile
import os

# setup
setup(name='warp10-jupyter',
      version='0.6',
      description='Jupyter extension that contains a cell magic to execute WarpScript code',
      url='http://github.com/senx/warp10-jupyter',
      author='Jean-Charles Vialatte',
      author_email='jean-charles.vialatte@senx.io',
      license='Apache 2.0',
      packages=['warpscript'],
      install_requires=['py4j', 'jupyter', 'requests', 'future'],
      setup_requires=['requests'],
      zip_safe=False)

# import requests after setup() eventually downloads it
import requests
from warpscript.warp10_version import TAR_PATH, URL, DIR, WARP10_JAR, WARP10_JAR_PATH

# download
if not(os.path.exists(TAR_PATH) or os.path.exists(WARP10_JAR_PATH)):
      r = requests.get(URL, stream = True)
      with open(TAR_PATH,"wb") as tarFile: 
            for chunk in r.iter_content(chunk_size=4096):  
                  if chunk: 
                        tarFile.write(chunk) 

# untar warp 10
if not(os.path.exists(WARP10_JAR_PATH)):
      with tarfile.open(TAR_PATH) as tarFile:
            tarFile.extract(WARP10_JAR, DIR)
if os.path.exists(TAR_PATH):
      os.remove(TAR_PATH)
