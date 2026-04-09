import xmlrpc.client as client

proxy = client.ServerProxy('http://127.0.0.1:12345', allow_none=True)

ime = None


for method_name in proxy.system.listMethods():
    print(f'{method_name} description: {proxy.system.methodHelp(method_name)}')
print(proxy.addition(2,3,5,8))
print(proxy.addition('a','b','c'))
#  print(proxy.quadratic(2, -4, 0))
#  print(proxy.remote_repr({"name": ime, "podatoci":{"godini":24, "pol":"zenski"}}))

# multicall = client.MultiCall(proxy)
# multicall.addition(2,3,5,8)
# multicall.addition('a','b','c')
# multicall.quadratic(2, -4, 0)

# for ans in multicall():
#     print(ans)