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

import os

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
