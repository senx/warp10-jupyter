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

"""Implements cell magics that execute WarpScript code.
"""

import re
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, line_cell_magic)
from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)
from IPython.core.display import (display, HTML)
from py4j.protocol import Py4JJavaError
import requests
from .warp10_gateway import Gateway

DEFAULT_ADDRESS = '127.0.0.1'
DEFAULT_PORT = 25333
DEFAULT_EXEC_ENDPOINT = 'https://warp.senx.io/api/v0/exec'

@magics_class
class WarpscriptMagics(Magics):
    """Holds magics related to WarpScript.
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

    @line_cell_magic
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
                help='If flag is used, do not print the output stack and log messages.')
    @argument('--replace', '-r',
                action='store_true',
                help='If flag is used, file paths surrounded by %% are replaced by their content. For example, %%token_file%% can be used not to expose a token in the notebook.') 
    @argument('--file', '-f',
                help='Path of a file which content is appended at the beginning of the WarpScript code.')
      
    def warpscript(self, line='', cell=''):
        """Instanciates or retrieves a WarpScript stack and interacts with it. Requires that the Warp 10 platform embed the Py4J plugin.
        """

        # parse inline arguments
        args = parse_argstring(self.warpscript, line)
        self.verbose = args.verbose

        # obtain gateway
        gateway = self.get_gateway(args.address, args.port)
        var = args.stack if not(args.stack is None) else gateway.default_stack_var

        # replace %file% patterns with file content
        if args.replace:
            cell = re.sub(r'%(\S*)%', lambda p: open(p.group(1), 'r').read(), cell)

        # append file at beginning
        if not(args.file is None):
            cell = open(args.file).read() + '\n' + cell

        # obtain stack and execute it
        if args.overwrite and var in gateway.stack_dict.keys():
            gateway.instance.detach(gateway.stack_dict[var])
            del gateway.stack_dict[var]
        stack = gateway.get_stack(var, self.verbose)
        try:
            stack.execMulti(cell)
        except Py4JJavaError as e:
            # don't raise an error when a stop exception is caught
            if not(gateway.instance.jvm.Class.forName("io.warp10.script.WarpScriptStopException").isInstance(e.java_exception)):
                raise e

        # store resulting stack
        self.shell.user_ns[var] = stack
        if self.verbose:
            return stack

    @line_cell_magic
    @magic_arguments()   
    @argument('--endpoint', '-e',
                default=DEFAULT_EXEC_ENDPOINT,
                help='The url of the exec endpoint')
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
                help='Path of a file which content is appended at the beginning of the WarpScript code.')
   
    def warp10exec(self, line='', cell=''):
        """Post WarpScript code to an exec endpoint and return a parsed JSON list.
        """

        # parse inline arguments
        args = parse_argstring(self.warp10exec, line)
        self.verbose = args.verbose

        # replace %file% patterns with file content
        if args.replace:
            cell = re.sub(r'%(\S*)%', lambda p: open(p.group(1), 'r').read(), cell)

        # append file at beginning
        if not(args.file is None):
            cell = open(args.file).read() + '\n' + cell

        # post WarpScript
        answer = requests.post(args.endpoint, cell)
        print('Status code:', answer.status_code)
        
        # store and output result
        if answer.status_code == 200:
            self.shell.user_ns[args.answer] = answer.json()
            if args.verbose:
                return self.shell.user_ns[args.answer]
        else:
            display(HTML(answer.text))
        