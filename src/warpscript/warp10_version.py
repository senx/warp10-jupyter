#
#   Copyright 2019  SenX S.A.S.
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

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()

import os
import tarfile
import requests

# version
REV = '2.1.0'

# current directory
DIR = os.path.abspath(os.path.dirname(__file__))

# tar.gz
TAR = 'warp10-' + REV +'.tar.gz'
TAR_PATH = os.path.abspath(os.path.join(DIR, TAR))

# jar
WARP10_JAR = os.path.join('warp10-' + REV, 'bin')
WARP10_JAR = os.path.join(WARP10_JAR, 'warp10-' + REV + '.jar')
WARP10_JAR_PATH = os.path.abspath(os.path.join(DIR, WARP10_JAR))

# url
REPO = 'https://dl.bintray.com/senx/generic/io/warp10/warp10/' + REV + '/'
URL = REPO + TAR

# download and get
def get_Warp10_jar_path():

    if not(os.path.exists(WARP10_JAR_PATH)):
        if not(os.path.exists(TAR_PATH)):
            print("Downloading Warp 10 archive ...")
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
    
    return WARP10_JAR_PATH
