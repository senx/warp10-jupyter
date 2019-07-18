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

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import range
from builtins import next
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object

import os
from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
from py4j.java_gateway import JavaObject
from py4j.java_gateway import get_method
from py4j.java_gateway import launch_gateway
from itertools import count

from .warp10_version import get_Warp10_jar_path

DEFAULT_LOCAL_LAUNCH_CONF = {}
DEFAULT_LOCAL_LAUNCH_CONF['warp.timeunits'] = 'us'
DEFAULT_LOCAL_LAUNCH_CONF['py4j.stack.nolimits'] = 'true'

class Gateway(object):
    """An object associated to a connection with a Java Gateway.
    It can hold multiple active WarpScript stacks.
    """

    ids = count(0)

    def __init__(self, addr, port, launch=False, auth_token=None, verbose=True, conf=DEFAULT_LOCAL_LAUNCH_CONF):

        self.instance = None
        self.entry_point = None

        self.addr = addr
        self.port = port
        self.launch = launch
        self.auth_token = auth_token
        self.verbose = verbose
        self.conf = conf # conf used by entry point when creating a stack
        self.address = addr + ':' + str(port)

        # gateway and entry point
        self.instance = self.get_instance()
        self.id = next(self.ids) # the id of the gateway
        self.entry_point = self.get_entry_point()

        # stack
        self.stack_dict = {} # store the stacks created by the Gateway
        self.default_stack_var = 'stack_' + str(self.id)

    def get_instance(self):
        if not(self.instance is None):
            return self.instance
        
        if self.launch:
            self.port, token = launch_gateway(enable_auth=True,die_on_exit=True,classpath=get_Warp10_jar_path())
            if self.verbose:
                print('Local gateway launched on port ' + str(self.port))
            instance = JavaGateway(gateway_parameters=GatewayParameters(port=self.port, auto_convert=True, auth_token=token))
        else:
            instance = JavaGateway(gateway_parameters=GatewayParameters(self.addr, self.port, auto_convert=True, auth_token=self.auth_token))
            if self.verbose:
                print('Establish connection with a gateway at ' + self.addr + ":" + str(self.port))
        
        return instance

    def get_entry_point(self):
        if not(self.entry_point is None):
            return self.entry_point

        if not(self.launch):
            # try to use an entry point that was started by a Warp 10 platform
            entry_point = self.get_instance().entry_point
            if not('newStack' in dir(entry_point)): # also, dir() raises an error if entry_point does not exist
                raise RuntimeError('Wrong entry point')
        else:
            # if locally launched, try to create an entry point provided warp10 jar is in the jvm classpath
            entry_point = self.get_instance().jvm.io.warp10.Py4JEntryPoint(self.conf)

        return entry_point

    def get_stack(self, var, verbose):
        """Create a WarpScript stack referenced under var,
        or retrieve existing one.
        """

        if var in globals():
            self.stack_dict[var] = eval(var)
            #if verbose:
                #print('Reuse WarpScript stack under variable "' + var + '".')

        if not(var in self.stack_dict.keys()):
            ep = self.get_entry_point()
            self.stack_dict[var] = ep.newStack()
            if verbose:
                print('Creating a new WarpScript stack accessible under variable "' + var + '".')
        #else:
            #if verbose:
                #print('Reuse WarpScript stack under variable "' + var + '".')
        
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
        lvl = count(1)
        ret = ''
        for l in self:
            c = str(next(lvl))
            if c == '1':
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