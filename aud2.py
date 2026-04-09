# Да се напише програма во која клиентите праќаат порака до серверот со која се
# регистрираат. Откако ќе се регистрираат, клиентите можат да праќаат пораки до друг
# клиент. Истовремено при праќање на порака, клиентите може да примаат пораки од страна
# на други клиенти. Препраќањето на пораките го врши серверот.

from socket import * #site funkcii koi rabotat so soketi
import sys, pickle, threading #sys za argumenti od komandna linija, pickle za objekti, threading za da moze serverot da raboti so povekje klienti istovremeno

s = socket(AF_INET, SOCK_DGRAM) # udp socket
MAX = 65535 
PORT = 7777

#kreirame klasa Klient koja ke gi cuva podatocite za klientot i razgovorite so drugi klienti
class Klient():
    def __init__(self, ime, prezime, korime, lozinka, adresa):
        self.ime = ime
        self.prezime, self.korime, self.lozinka, self.adresa = prezime, korime, lozinka, adresa
        self.razgovori = {} # {"korime1": ["poraka1", "poraka2", ..], "":[], ...}

    def dodajPoraka(self, poraka, k):
        if k in self.razgovori:
            self.razgovori[k] += [poraka]
        else:
            self.razgovori[k] = []
            self.razgovori[k] += [poraka]

def klientCekaj(s):
    while True:
        data, addr = s.recvfrom(MAX)
        print(data.decode())


if sys.argv[-1] == 'server':
    klienti = {} # {"korime1": Klient1, "korime2": Klient2, ...}
    s.bind(('127.0.0.1', PORT))
    print(f'Listening at {s.getsockname()}')
    
    while True:
        data, addr = s.recvfrom(MAX)
        data = pickle.loads(data)
        if data["reg"] == 1:
            if data['korime'] in klienti:
                s.sendto('Korisnickoto ime e zafateno, porbajte drugo. '.encode(), addr)
            else:
                klienti[data['korime']]=Klient(data['ime'], data['prezime'], data['korime'], data['lozinka'], addr)
                s.sendto('Uspeshna najava! '.encode(), addr)
        elif data["reg"] == 0:
            if data['to'] in klienti: # data['to'] e username na primac
                for klient in klienti.values():
                    if klient.adresa == addr:
                        sender = klient.korime
                        break
                s.sendto((sender + ": " + data['msg']).encode(), klienti[data['to']].adresa)
                klienti[data['to']].dodajPoraka(data['msg'], sender)
                s.sendto('Uspeshno pratena poraka! '.encode(), addr)
            else:
                s.sendto('Toj korisnik ne e registriran, probaj pak! '.encode(), addr)

elif sys.argv[-1] == 'client':
    ime = input('Vnesi ime: ')
    prezime = input('Vnesi prezime: ')
    while True:
        korime = input('Vnesi korisnicko ime: ')
        lozinka = input('Vnesi lozinka: ')
        msg = {"reg":1, "ime":ime, "prezime":prezime, "korime":korime, "lozinka":lozinka}
        msg = pickle.dumps(msg)
        s.sendto(msg, ('127.0.0.1', PORT))
        ans, _ = s.recvfrom(MAX)
        print(ans.decode())
        if ans.decode() == 'Uspeshna najava! ':
            break
    
    threading.Thread(target=klientCekaj,args=(s,)).start()
    while True:
        # prakanje na poraki
        to = input('Do kogo? ')
        poraka = input('Vnesi poraka: ')
        msg = {"reg":0, "to":to, "msg":poraka}
        msg = pickle.dumps(msg)
        s.sendto(msg, ('127.0.0.1', PORT))

else:
    print(sys.stderr, 'usage: python3 <filename> client/server')

#
'''
Klasata klient ja kreirame za da cuva povekje info za sekoj korisnik na serverot
site korisnici da se na edno mesto i da ne se cuva samo username tuku i dr podatoci 
zatoa se definiraat kako objekti
- init() se cuva ime i prezime, username=korime, lozinka i adresa
- so self.razgovori se cuvaat razgovorite so drugi klienti, dictionary od tip usarename:poraki, poraki e lista od poraki so toj korisnik
    self ozncuva dadeniot objekt vo toj moment
- dodajPoraka() funkcija koja se koristi za da se dodade poraka 
'''