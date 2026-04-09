import xmlrpc.client as client
from socket import *
import struct, pickle, threading

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

proxy = client.ServerProxy('http://127.0.0.1:12345')

najaven_vo_sesija = 0 # flag za sesija na korisnicka strana (optional)

while True:
    cmd = input("<<<\nRegistracija - r \n Najava - n \n Odjava - o \n Kreiraj grupa - kg\
                 \n Prikluci grupa - pg \n Isprati do korisnik - ik \n Isprati do grupa - ig \
                \n Prati trud - pt \n Vidi trudovi - vt \n Napushti grupa - ng \n Odjava - o\n>>>")

    if cmd == 'r':
        ime = input("Vnesi ime: ")
        korime = input('Vnesi username: ')
        pasvord = input("Vnesi pass: ")
        pozicija = input("Vnesi pozicija: ")
        print(proxy.registracija(pozicija, ime, korime, pasvord))

    if cmd == 'n':
        if najaven_vo_sesija:
            print('Najaveni ste.')
        else:
            korime = input("Vnesi username: ")
            pasvord = input("Vnesi passowrd: ")
            s = socket(AF_INET, SOCK_STREAM)
            s.bind(('127.0.0.1',0))
            print(s.getsockname())
            threading.Thread(target=slusaj,args=(s,)).start()
            odgovor = proxy.najava(korime,pasvord,s.getsockname()[0],s.getsockname()[1])
            print(odgovor)
            if odgovor == "Uspeshno se najavivte.":
                najaven_vo_sesija = 1

    if cmd == 'kg':
        ime = input("Vnesi ime na grupata sto ja kreirash: ")
        print(proxy.kreiraj_grupa(korime,ime))

    if cmd == 'pg':
        ime = input("Vnesi ime na grupata kade sakas da se priklucis: ")
        print(proxy.prikluci_grupa(korime,ime))

    if cmd == 'bg':
        ime = input("Vnesi ime na grupata koja sakas da ja izbrishesh: ")
        print(proxy.kreiraj_grupa(korime,ime))

    if cmd == 'ik':
        dokogo = input("Vnesi dokogo: ")
        if isinstance(proxy.isprati_korisnik(korime, dokogo),str):
            print(proxy.isprati_korisnik(korime, dokogo))
        else:
            addr, porta = proxy.isprati_korisnik(korime, dokogo)

            sp2p = socket(AF_INET,SOCK_STREAM)
            sp2p.connect((addr,porta))
            poraka = input("Vnesi poraka: ")
            full_msg = struct.pack("!i",len(poraka.encode()))+poraka.encode()
            sp2p.send(full_msg)
            sp2p.close()
    
    if cmd == 'ig':
        ime = input("Do koja grupa? ")
        clenovi = proxy.isprati_grupa(korime, ime)
        if isinstance(clenovi,str):
            print(clenovi)
        else:
            poraka = input("Vnesi poraka: ")
            full_msg = struct.pack("!i",len(poraka.encode()))+poraka.encode()
            for clen in clenovi:
                addr, porta = clenovi[clen]
                sg = socket(AF_INET,SOCK_STREAM)
                sg.connect((addr,porta))
                sg.send(full_msg)
                sg.close()

    if cmd == 'pt':
        naslov = input("Vnesi naslov na trudot")
        link = input("Vnesi go linkot")
        print(proxy.prati_trud(korime,naslov,link))

    if cmd == 'vt':
        trudovi = proxy.vidi_trudovi(korime)
        if isinstance(trudovi,dict):
            for trud in trudovi:
                print(f"{trud}: {trudovi[trud]}")
        else:
            print(trudovi)

    if cmd == 'ng':
        ime_grupa = input('Od koja grupa sakate da izlezete? ')
        print(proxy.napusti_grupa(ime_grupa, korime))

    if cmd == 'o':
        print(proxy.odjava(korime))
        najaven_vo_sesija = 0
