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

from py4j import protocol as proto
from py4j.protocol import register_output_converter
from py4j.java_gateway import launch_gateway, JavaGateway, GatewayParameters
from .warpscript_magics import WarpscriptMagics
from .warpscript_magics import DEFAULT_GATEWAY_ADDRESS, DEFAULT_GATEWAY_PORT
from .warp10_gateway import convert, DEFAULT_LOCAL_LAUNCH_CONF
from .warp10_version import get_Warp10_jar_path

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

# Create stack not associated to a notebook or to a variable name
# Each of these stacks creates a new gateway connection
def newStack(addr=DEFAULT_GATEWAY_ADDRESS, port=DEFAULT_GATEWAY_PORT, auth_token=None):
    """Creates a new stack from a remote gateway spawned by a Warp 10 platform
    """

    gateway = JavaGateway(gateway_parameters=GatewayParameters(addr, port, auto_convert=True, auth_token=auth_token))
    return gateway.entry_point.newStack()

def newLocalStack(conf=DEFAULT_LOCAL_LAUNCH_CONF, classpath=get_Warp10_jar_path()):
    """Creates a new stack locally (not connected by a Warp 10 platform)
    """

    port, auth_token = launch_gateway(enable_auth=True,die_on_exit=True,classpath=classpath)
    gateway = JavaGateway(gateway_parameters=GatewayParameters(port=port, auto_convert=True, auth_token=auth_token))
    entry_point = gateway.jvm.io.warp10.Py4JEntryPoint(conf)
    return entry_point.newStack()