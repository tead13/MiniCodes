from xmlrpc.server import SimpleXMLRPCServer
import math
from functools import reduce
import operator

def addition(*args):
    """Vraka suma na dadeni vlezni argumenti"""
    return reduce(operator.add,args),
    #return sum(args)

def quadratic(a,b,c):
    """Reshava kvadratna ravenka"""
    # -b +/- √(b^2-4ac) / 2a
    d = math.sqrt(math.pow(b,2)-4*a*c)
    return list(set([(-b+d)/(2*a),(-b-d)/(2*a)]))

def remote_repr(arg):
    """Vraka string reprezentacija na vlezen argument arg"""
    return repr(arg)

server = SimpleXMLRPCServer(('127.0.0.1',12345), allow_none=True)

server.register_function(addition)
server.register_function(quadratic)
server.register_function(remote_repr)

server.register_introspection_functions()
# listMethods(), methodHelp(), methodSignature()

server.register_multicall_functions() #povekje povivi na funk vo ist moment,  vo eden

print('Server up and listening..')
server.serve_forever()