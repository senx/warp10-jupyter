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

"""Implements cell magics related to WarpScript and Warp 10.

    %%warpscript
    %%warp10exec
    %%warp10update
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import super
from builtins import str
from builtins import open
from future import standard_library
standard_library.install_aliases()

import re
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, line_cell_magic)
from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)
from IPython.core.display import (display, HTML)
from py4j.protocol import Py4JJavaError
from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
import requests
from .warp10_gateway import Gateway

DEFAULT_GATEWAY_ADDRESS = '127.0.0.1'
DEFAULT_GATEWAY_PORT = 25333
DEFAULT_EXEC_ENDPOINT = 'https://warp.senx.io/api/v0/exec'
DEFAULT_UPDATE_ENDPOINT = 'http://127.0.0.1:8080/api/v0/update'

@magics_class
class WarpscriptMagics(Magics):

    def __init__(self, shell):
        super(WarpscriptMagics, self).__init__(shell)
        self.gateway_dict = {} # the keys are ip:port or local
        self.last_var = ''

    def get_gateway(self, addr, port, launch, auth_token, verbose):
        key = 'local' if launch else addr + ':' + str(port)
        if not(key in self.gateway_dict.keys()):
            self.gateway_dict[key] = Gateway(addr, port, launch, auth_token, verbose)

        return self.gateway_dict[key]

    @line_cell_magic
    @magic_arguments()
    @argument('--stack', '-s',
                default="stack",
                help='The variable that references the WarpScript stack. Default to "stack".')
    @argument('--overwrite', '-o',
                action='store_true',
                help='If flag is used, overwrite any object referenced under given variable with a new stack.')
    @argument('--address', '-a',
                default=DEFAULT_GATEWAY_ADDRESS,
                help='The ip address of the gateway to connect to. Default to 127.0.0.1.')
    @argument('--port', '-p',
                default=DEFAULT_GATEWAY_PORT,
                help='The corresponding port of the gateway. Default to 25333.')
    @argument('--authtoken', '-t',
                help='Authentication token used for gateway connection if requested.')
    @argument('--local', '-l',
                dest='launch',
                action='store_true',
                help='Launch a secured local gateway instead of trying to connect to one. If launched this way, it is not connected to a Warp 10 platform.')
    @argument('--not-verbose', '-v',
                dest='verbose',
                action='store_false',
                help='Do not print stack and log messages.')
    @argument('--replace', '-r',
                action='store_true',
                help='If used, file paths surrounded by %% are replaced by their content. For example, %%token_file%% can be used not to expose a token in the notebook.') 
    @argument('--file', '-f',
                help='A file path. WarpScript code from this file will be executed before any WarpScript code from the cell.')
      
    def warpscript(self, line='', cell=''):
        """Instanciates or retrieves a WarpScript execution environment (a stack) and executes code with it.
        """

        # parse inline arguments
        args = parse_argstring(self.warpscript, line)
        self.verbose = args.verbose

        # replace %file% patterns with file content
        if args.replace:
            cell = re.sub(r'%(\S*)%', lambda p: open(p.group(1), 'r').read(), cell)

        # append file at beginning
        if not(args.file is None):
            cell = open(args.file).read() + '\n' + cell

        # delete stack if overwrite
        var = args.stack
        if args.overwrite and var in self.shell.user_ns:
            del self.shell.user_ns[var]

        # obtain stack from variable if it is already referenced
        if var in self.shell.user_ns:
            stack = self.shell.user_ns[var]
            #if self.verbose:
                #print('Reuse WarpScript stack under variable "' + var + '".')

        # or obtain it from a gateway
        else:

            # obtain gateway
            gateway = self.get_gateway(args.address, args.port, args.launch, args.authtoken, args.verbose)
            var = args.stack if not(args.stack is None) else gateway.default_stack_var

            # obtain stack
            if args.overwrite and var in gateway.stack_dict.keys():
                gateway.instance.detach(gateway.stack_dict[var])
                del gateway.stack_dict[var]
            stack = gateway.get_stack(var, self.verbose)

        # execute WarpScript code
        try:
            stack.execMulti(cell)
        except Py4JJavaError as e:
            # don't raise an error when a stop exception is caught
            if not('gateway' in vars()):
                gw = JavaGateway(stack._gateway_client, auto_convert=True)
            else:
                gw = gateway.instance
            if not(gw.jvm.Class.forName("io.warp10.script.WarpScriptStopException").isInstance(e.java_exception)):
                raise e

        # store resulting stack
        self.shell.user_ns[var] = stack
        if self.verbose:
            return stack

    @line_cell_magic
    @magic_arguments()
    @argument('--endpoint', '-e',
                default=DEFAULT_EXEC_ENDPOINT,
                help='The url of the exec endpoint. Default to https://warp.senx.io/api/v0/exec.')
    @argument('--answer', '-a',
                default='response',
                help='The variable that store the result. Default to "response".')
    @argument('--not-verbose', '-v',
                dest='verbose',
                action='store_false',
                help='If flag is used, do not output the JSON response.')
    @argument('--replace', '-r',
                action='store_true',
                help='If flag is used, file paths surrounded by %% are replaced by their content. For example, %%token_file%% can be used not to expose a token in the notebook.')
    @argument('--file', '-f',
                help='Path of a file from which content is appended at the beginning of the WarpScript code.')
   
    def warp10exec(self, line='', cell=''):
        """Post WarpScript code to an exec endpoint and return a parsed JSON list.
        """

        # parse inline arguments
        args = parse_argstring(self.warp10exec, line)

        # replace %file% patterns with file content
        if args.replace:
            cell = re.sub(r'%(\S*)%', lambda p: open(p.group(1), 'r').read(), cell)

        # append file at beginning
        if not(args.file is None):
            cell = open(args.file).read() + '\n' + cell

        # post WarpScript
        answer = requests.post(args.endpoint, cell)
        
        # store and output result
        if answer.status_code == 200:
            print('Status code:', answer.status_code)
            self.shell.user_ns[args.answer] = answer.json()
            if args.verbose:
                return self.shell.user_ns[args.answer]
        else:
            display(HTML(answer.text))

    @line_cell_magic
    @magic_arguments()
    @argument('--endpoint', '-e',
                default=DEFAULT_UPDATE_ENDPOINT,
                help='The url of the update endpoint. Default to http://127.0.0.1:8080/api/v0/update.')
    @argument('--token', '-t',
                help='Write token.')
    @argument('--gzip', '-g',
                action='store_true',
                help='If flag is used, use gzip encoding.')
    @argument('--file', '-f',
                help='Path containing data points to push.')

    def warp10update(self, line='', cell=None):
        """Push data points from file then/or cell.
        """

        # parse inline arguments
        args = parse_argstring(self.warp10update, line)
        headers = {'X-Warp10-Token': args.token}
        if args.gzip:
            headers['Accept-Encoding'] = 'gzip'

        # post data points
        if not(args.file is None):
            print('Pushing data points from file ...')
            answer = requests.post(args.endpoint, headers=headers, data=open(args.file))
            if answer.status_code == 200:
                print('Status code:', answer.status_code)
            else:
                display(HTML(answer.text))
        if not(cell is None):
            print('Pushing data points from cell ...')
            answer = requests.post(args.endpoint, headers=headers, data=cell)
            if answer.status_code == 200:
                print('Status code:', answer.status_code)
            else:
                display(HTML(answer.text))
