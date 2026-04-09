from  socket import *

HOST = input('Vnesi hostname: ')
PORT = 80
MAX = 6000

s = socket(AF_INET,SOCK_STREAM)
s.connect((HOST,PORT))

request = ("GET / HTTP/1.1\r\n"
           f"Host: {HOST}\r\n"
           "Connection: close\r\n"
           "\r\n"
           )

s.sendall(request.encode())

while True:
    ans = s.recv(MAX)
    if not ans:
        break
    print(ans.decode(errors='ignore'))

s.close()

# Start Wireshark, listen on interface WiFi and instert capture filter 'port 80'
# Open cmd and type ipconfig to list the interfaces (find WiFi)
# start the script ->
# Enter the target host name to connect:  www.linux.org
# Enter the target port: 80
# Stop and analyze Wireshark
# test the script with different inputs for hostname and port.. 
# (testing different ports would mean changing it to a variable in the script, and capturing on different ports in Wireshark)