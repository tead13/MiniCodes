from socket import *
import threading, struct, pickle

s = socket(AF_INET,SOCK_STREAM) # normalen rezim
ss = socket(AF_INET, SOCK_STREAM) # pasiven rezim
ss.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
PORT = 12345
server = ('127.0.0.1', PORT)

ss.bind(('127.0.0.1',0))
print(f'Mojot soket za slushanje e: {ss.getsockname()}')

statii = {} # { "Naslov1" : "Tekst od statijata Naslov 1", "Naslov2" : "Tekst od statijata Naslov 2" }

def recv_all(sc, msg_len):
    data = b''
    while len(data)< msg_len:
        more = sc.recv(msg_len - len(data))
        if not more:
            raise EOFError(f'read {len(data)} from {msg_len}B message.')
        data += more
    return data

def slusaj(ss):
    # prima konekcii od drugi klienti (p2p)
    ss.listen()
    while True:
        s_client, addr = ss.accept()
        baran_naslov = recv_all(s_client,struct.unpack("!i",recv_all(s_client,4))[0]).decode()
        if baran_naslov in statii:
            s_client.sendall(struct.pack("!i",len(statii[baran_naslov].encode()))+statii[baran_naslov].encode())
        else:
            s_client.sendall(struct.pack("!i",len('Ne postoi takov tekst.'.encode()))+'Ne postoi takov tekst.'.encode())
        s_client.close()

def vnesiStatii():
    # Staveno vo funkcija za da se ovozmozi vnesuvanje na novi naslovi od korisnikot 
    # - se povikuva sekogas koga ke se izbere 'konekcija'
    n = input('Vnesi broj na statii: ')
    for i in range(int(n)):
        naslov = input('Vnesi naslov: ')
        tekst = input('Vnesi tekst: ')
        statii[naslov] = tekst

s.connect(server)

threading.Thread(target = slusaj, args=(ss,)).start()
while True:
    cmd = input('Konekcija do server ili prebaruvanje? ')
    if cmd == 'konekcija':
        vnesiStatii()
        naslovi = list(statii.keys())
        poraka = 'konekcija|'+ ss.getsockname()[0] + '|' + str(ss.getsockname()[1])
        poraka = poraka.encode()
        full_msg = struct.pack("!i",len(poraka)) + poraka
        s.sendall(full_msg)
        dolzina = struct.unpack("!i",recv_all(s,4))[0]
        odgovor = recv_all(s,dolzina).decode()
        print(odgovor)
        naslovi_tosend = pickle.dumps(naslovi)
        full_msg = struct.pack("!i",len(naslovi_tosend)) + naslovi_tosend
        s.sendall(full_msg)
        dolzina = struct.unpack("!i",recv_all(s,4))[0]
        odgovor = recv_all(s,dolzina).decode()
        print(odgovor)
    elif cmd == 'prebaruvanje':
        # P2P
        naslov = input("Vnesi naslov: ")
        if naslov not in statii:
            baranje = cmd + '|' + naslov
            s.sendall(struct.pack("!i",len(baranje.encode())) + baranje.encode())
            odgovor = recv_all(s,struct.unpack("!i",recv_all(s,4))[0]).decode().split("|")
            if odgovor[0] == 'OK':
                # odgovor = 'OK|adresa|porta'  - na korisnikot koj ja ima statijata
                print(f'server: {odgovor[0]}, statijata baraj ja od klientot so adresa {odgovor[1]}:{odgovor[2]}')
                s_p2p = socket(AF_INET,SOCK_STREAM)
                s_p2p.connect((odgovor[1],int(odgovor[2])))
                s_p2p.sendall(struct.pack("!i",len(naslov.encode())) + naslov.encode())
                tekst = recv_all(s_p2p,struct.unpack("!i",recv_all(s_p2p,4))[0])
                print(f'\'{odgovor[1]}:{odgovor[2]}\': Tekstot na baranata statija e: ')
                print(tekst.decode())
                s_p2p.close()

                statii[naslov] = tekst.decode()
            elif odgovor[0] == 'Greska':
                # odgovor = 'Greska|Nema takva statija.'
                print(odgovor[1])
        else:
            print('Statijata se naoga na tvojata adresa.')