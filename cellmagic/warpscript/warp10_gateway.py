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

from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
from py4j.java_gateway import JavaObject
from py4j.java_gateway import get_method
from itertools import count

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

        if var in vars():
            self.stack_dict[var]

        if not(var in self.stack_dict.keys()):
            # try first to use an entry point that was started in the Java side
            try:
                self.stack_dict[var] = self.instance.entry_point.newStack()
            except:
                self.stack_dict[var] = self.instance.jvm.io.warp10.Py4JEntryPoint({'warp.timeunits': 'us' })
            if verbose:
                print('Creating a new WarpScript stack accessible under variable "' + var + '".')
        return self.stack_dict[var]

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
        if len(self):
            return self.getName() + self.getLabels().toString() + '<' + self.getType().toString() + ', ' + str(len(self)) + ' values>'
        else:
            return self.getName() + self.getLabels().toString() + '<empty>'

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