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

from py4j import protocol as proto
from py4j.protocol import register_output_converter
from .warpscript_magics import WarpscriptMagics
from .warp10_gateway import convert

def load_ipython_extension(ipython):
    """Allow this package to be loaded as a Jupyter extension.
    """
    magics = WarpscriptMagics(ipython)
    ipython.register_magics(magics)
    ipython.magics_manager.register_alias('mc2', 'warpscript', 'cell')
    ipython.magics_manager.register_alias('mc2', 'warpscript', 'line')

# Register conversion of Stack and Gts objects in Py4J protocol
register_output_converter(
    proto.REFERENCE_TYPE, lambda target_id, gateway_client:
    convert(target_id, gateway_client))