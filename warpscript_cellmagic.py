from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)
from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)
from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
from itertools import count

DEFAULT_ADDRESS = '127.0.0.1'
DEFAULT_PORT = 25333

class Gateway():
    ids = count(0)

    def __init__(self, addr, port):
        self.instance = JavaGateway(gateway_parameters=GatewayParameters(addr, port, auto_convert=True))
        self.address = addr + ':' + str(port)
        self.stack_dict = {} # store the stacks created by the Gateway
        self.id = next(self.ids) # the id of the gateway
        self.default_stack_var = 'stack_' + str(self.id)
        
    def get_stack(self, var):
        if not(var in self.stack_dict.keys()):
            self.stack_dict[var] = self.instance.entry_point.newStack()
            print('A WarpScript stack has been created at ' + self.address + ' and is stored under variable "' + var + '".')
        return self.stack_dict[var]

@magics_class
class WarpscriptMagics(Magics):

    def __init__(self, shell):
        super(WarpscriptMagics, self).__init__(shell)
        self.gateway_dict = {} # the keys are ip:port

    def get_gateway(self, addr, port):
        key = addr + ':' + str(port)
        if not(key in self.gateway_dict.keys()):
            self.gateway_dict[key] = Gateway(addr, port)
            print('A client connected to the Java gateway at ' + key + ' has been created.')
        return self.gateway_dict[key]

    @cell_magic
    @magic_arguments()
    @argument('--stack', '-s',
                help='The variable that store the resulting WarpScript stack. For each Java gateway, a new variable name creates a new stack. Default to "stack_<gateway_id>".')
    @argument('--address', '-a',
                default=DEFAULT_ADDRESS,
                help='The ip address of the Java gateway with the Warp10 instance. Default to 127.0.0.1.')
    @argument('--port', '-p',
                default=DEFAULT_PORT,
                help='The corresponding port of the Java gateway. Default to 25333.')
    def warpscript(self, line='', cell=None):
        args = parse_argstring(self.warpscript, line)
        gateway = self.get_gateway(args.address, args.port)
        var = args.stack if not(args.stack is None) else gateway.default_stack_var
        stack = gateway.get_stack(var)
        stack.execMulti(cell)
        self.shell.user_ns[var] = stack
        print('The WarpScript stack at ' + gateway.address + ' stored under variable "' + var + '" has been executed.')

def load_ipython_extension(ipython):
    magics = WarpscriptMagics(ipython)
    ipython.register_magics(magics)