from socket import *
import struct,sys, threading

s = socket(AF_INET, SOCK_STREAM)

def recv_all(sc, msg_len):
    data = b''
    while len(data)< msg_len:
        more = sc.recv(msg_len - len(data))
        if not more:
            raise EOFError(f'read {len(data)} from {msg_len}B message.')
        data += more
    return data

def cekaj(s):
    while True:
        length = struct.unpack("!i",recv_all(s,4))[0]
        data = recv_all(s,length).decode()
        print(data)

s.connect(('127.0.0.1', 7777))

username = input('Vnesete korisnicko ime: ')
msg = "registracija|"+username
msg_encoded = msg.encode()
length = len(msg_encoded)
full_msg = struct.pack("!i",length) + msg_encoded

s.sendall(full_msg)

dolzina = recv_all(s,4)
dolzina = struct.unpack("!i",dolzina)[0]
ans = recv_all(s,dolzina)

ans = ans.decode()

if ans == "Neuspeshno!":
    print('Neuspeshna registracija!')
    sys.exit(-1)
else:
    print('Uspeshna regstracija!')
    try:
        t = threading.Thread(target=cekaj, args=(s,))
        t.start()
        while True:
            dokogo = input('Vnesi username na primac! ')
            poraka = input('Vnesi poraka: ')
            msg = 'porakado|'+dokogo+'|'+poraka+"|"+username
            msg = msg.encode()
            dolz = struct.pack("!i",len(msg))

            fullmsg = dolz+msg
            s.sendall(fullmsg)
    except:
        print('Nekoja greshka..')
        sys.exit(-1)


