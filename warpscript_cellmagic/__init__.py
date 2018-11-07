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

"""Jupyter extension that contains a cell magic to execute WarpScript code.
"""

from collections import MutableSequence
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)
from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)
from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
from py4j.java_gateway import JavaObject
from py4j.java_gateway import get_method
from py4j.java_collections import JavaList
from py4j import protocol as proto
from py4j.protocol import get_command_part
from py4j.protocol import get_return_value
from py4j.protocol import register_output_converter
from itertools import count

def load_ipython_extension(ipython):
    """Allow this file to be loaded as a Jupyter extension.
    """
    magics = WarpscriptMagics(ipython)
    ipython.register_magics(magics)

DEFAULT_ADDRESS = '127.0.0.1'
DEFAULT_PORT = 25333

class Gateway():
    """An object associated to a connection with a Java Gateway.
    It can hold multiple active WarpScript stacks.
    """

    ids = count(0)

    def __init__(self, addr, port):
        self.instance = JavaGateway(gateway_parameters=GatewayParameters(addr, port, auto_convert=True))
        self.address = addr + ':' + str(port)
        self.stack_dict = {} # store the stacks created by the Gateway
        self.id = next(self.ids) # the id of the gateway
        self.default_stack_var = 'stack_' + str(self.id)
        
    def get_stack(self, var, verbose):
        """Create a WarpScript stack referenced under var,
        or retrieve existing one.
        """

        if not(var in self.stack_dict.keys()):
            self.stack_dict[var] = self.instance.entry_point.newStack()
            if verbose:
                print('Creating a new WarpScript stack accessible under variable "' + var + '".')
        return self.stack_dict[var]

@magics_class
class WarpscriptMagics(Magics):
    """Holds the cell magic '%%warpscript'.
    """

    def __init__(self, shell):
        super(WarpscriptMagics, self).__init__(shell)
        self.gateway_dict = {} # the keys are ip:port
        self.verbose = True

    def get_gateway(self, addr, port):
        """Create a connection with a Java gateway located at specified address,
        or retrieve existing one.
        """

        key = addr + ':' + str(port)
        if not(key in self.gateway_dict.keys()):
            self.gateway_dict[key] = Gateway(addr, port)
            if self.verbose:
                print('Starting connection with ' + key + '.')
        return self.gateway_dict[key]

    @cell_magic
    @magic_arguments()
    @argument('--stack', '-s',
                help='The variable that store the resulting WarpScript stack. For each connection, a new variable name creates a new stack. Default to "stack_<gateway_id>".')
    @argument('--overwrite', '-o',
                action='store_true',
                help='If flag is used, overwrite existing stack stored under used variable with a new one.')
    @argument('--address', '-a',
                default=DEFAULT_ADDRESS,
                help='The ip address of the gateway connected to the Warp 10 platform or WarpScript module. Default to 127.0.0.1.')
    @argument('--port', '-p',
                default=DEFAULT_PORT,
                help='The corresponding port of the gateway. Default to 25333.')
    @argument('--not-verbose', '-v',
                dest='verbose',
                action='store_false',
                help='If flag is used, do not print the stack and log messages.')
   
    def warpscript(self, line='', cell=None):
        """Executes WarpScript code.
        """

        # parse inline arguments
        args = parse_argstring(self.warpscript, line)
        self.verbose = args.verbose

        # obtain gateway
        gateway = self.get_gateway(args.address, args.port)
        var = args.stack if not(args.stack is None) else gateway.default_stack_var

        # obtain stack and execute it
        if args.overwrite and var in gateway.stack_dict.keys():
            del gateway.stack_dict[var]
        stack = gateway.get_stack(var, self.verbose)
        stack.execMulti(cell)

        # store resulting stack
        self.shell.user_ns[var] = stack
        if self.verbose:
            print(repr(stack))

class Stack(JavaObject):
    """A wrapper of a WarpScript stack with implementations for for python print, repr and len.
    """

    def __init__(self, jObj):
        JavaObject.__init__(self, jObj._target_id, jObj._gateway_client)

    def __len__(self):
        return self.depth()

    def __iter__(self):
        for l in range(len(self)):
            yield self.get(l)
    
    def __repr__(self):
        lvl = count(0)
        ret = ''
        for l in self:
            c = str(next(lvl))
            if c == '0':
                ret += 'top: \t' + repr(l) +'\n'
            else:
                ret += c + ': \t' + repr(l) +'\n'
        return ret

    def __str__(self):
        listRep = [l for l in self]
        listRep.reverse()
        return 'Stack(' + str(listRep) + ')'

class Gts(JavaObject):
    """A wrapper of a Geo Time Serie with implementation for python print, repr and len.
    """

    def __init__(self, jObj):
        JavaObject.__init__(self, jObj._target_id, jObj._gateway_client)
        self.max_repr_len = 60
        #self.gateway = JavaGateway(self._gateway_client)

    def __len__(self):
        return self.size()

    def full_repr(self):
        return self.toString()[:-1].replace('\n=', ', ')
    
    def __repr__(self):
        return '<GTS with ' + str(len(self)) + ' values>'

    def __str__(self):
        return 'Gts(' + self.full_repr() + ')'

    # The following methods are examples should you need to extend this object using Java nethods
    """
    def valueAtIndex(self, index):
        return self.gateway.jvm.io.warp10.continuum.gts.GTSHelper.valueAtIndex(self, index)

    def valueAtTick(self, tick):
        return self.gateway.jvm.io.warp10.continuum.gts.GTSHelper.valueAtTick(self, tick)
    
    def tickAtIndex(self, index):
        return self.gateway.jvm.io.warp10.continuum.gts.GTSHelper.tickAtIndex(self, index)

    def __iter__(self):
        for index in range(len(self)):
            yield self.valueAtIndex(index)
    
    def values(self):
        return [val for val in self]

    def ticks(self):
        return [self.tickAtIndex(index) for index in range(len(self))]

    def toNumpyArray(self):
        try:
            import numpy as np
        except ImportError:
            raise RuntimeError('You need to install numpy to use method toNumpyArray()')
        # Do something here
    """

def convert(target_id, gateway_client):
    """Convert WarpScript stacks and GTS into wrapped objects.
    """

    jObject = JavaObject(target_id, gateway_client)

    # check if it is a WarpScript stack
    if 'execMulti' in dir(jObject):
        return Stack(jObject)
    
    # check if it is a GTS
    elif 'hasElevations' in dir(jObject):
        return Gts(jObject)

    else:
        return jObject

register_output_converter(
    proto.REFERENCE_TYPE, lambda target_id, gateway_client:
    convert(target_id, gateway_client))