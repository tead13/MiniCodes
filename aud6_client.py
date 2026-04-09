from socket import *
import xmlrpc.client as client
import threading
import struct

s = socket(AF_INET,SOCK_STREAM)
proxy = client.ServerProxy('http://127.0.0.1:12345')

def recv_all(sc, msg_len):
    data = b''
    while len(data)< msg_len:
        more = sc.recv(msg_len - len(data))
        if not more:
            raise EOFError(f'read {len(data)} from {msg_len}B message.')
        data += more
    return data

def slusaj(s):
    s.listen(5)
    while True:
        sp2p, _ = s.accept()
        poraka = recv_all(sp2p,struct.unpack("!i",recv_all(sp2p,4))[0]).decode()
        print(poraka)
        sp2p.close()

while True:
    cmd = input("<<<\nRegistracija - r \n Najava - n \n Odjava - o \n Kreiraj grupa - kg \n Prikluci grupa - pg \n Isprati do korisnik - ik \n Isprati do grupa - ig\n>>>")
    if cmd == 'r':
        korime = input("Vnesi username: ")
        lozinka = input("Vnesi password: ")
        print(proxy.registracija(korime,lozinka))

    if cmd == 'n':
        korime = input("Vnesi username: ")
        lozinka = input("Vnesi passowrd: ")
        s.bind(('127.0.0.1',0))
        print(s.getsockname())
        threading.Thread(target=slusaj,args=(s,)).start()
        print(proxy.najava(korime,lozinka,s.getsockname()[0],s.getsockname()[1]))

    if cmd == 'o':
        print(proxy.odjava(korime))
    
    if cmd == 'kg':
        ime = input("Vnesi ime na grupata: ")
        print(proxy.kreiraj_grupa(ime))

    if cmd == 'pg':
        ime = input("Vnesi ime na grupata kade sakas da se priklucis: ")
        print(proxy.prikluci_grupa(ime,korime))

    if cmd == 'ik':
        dokogo = input("Vnesi uname do kogo ke prakas: ")
        if proxy.prati_korisnik(korime,dokogo) != "Ne ste najaveni ili korisnikot do koj sakate da pratite ne e najavi.":
            addr, port = proxy.prati_korisnik(korime, dokogo)
            sp = socket(AF_INET, SOCK_STREAM)
            sp.connect((addr,port))
            poraka = input("Vnesi poraka: ")
            msg = ("\n"+korime+ ": " + poraka).encode()
            sp.sendall(struct.pack("!i",len(msg))+msg)
            sp.close()
        else:
            print(proxy.prati_korisnik(korime, dokogo))
        
    if cmd == 'ig':
        dokoja= input("ime na grupa: ")
        clenovi = proxy.isprati_grupa(korime, dokoja)
        print(type(clenovi))
        poraka = input("Vnesi poraka: ")
        msg = ("grupa \'"+dokoja+"\' | "+korime+ ": " + poraka).encode()
        full_msg = struct.pack("!i",len(msg))+msg

        for clen in clenovi:
            addr, porta = clenovi[clen]
            if addr == s.getsockname()[0] and int(porta) == s.getsockname()[1]:
                continue
            spc = socket(AF_INET,SOCK_STREAM)
            spc.connect((addr,int(porta)))
            spc.sendall(full_msg)
            spc.close()
        
