# Да се напише програма во која клиентите праќаат порака до серверот со која се
# регистрираат. Откако ќе се регистрираат, клиентите можат да праќаат пораки до друг
# клиент. Истовремено при праќање на порака, клиентите може да примаат пораки од страна
# на други клиенти. Препраќањето на пораките го врши серверот.

from socket import *
import sys, pickle, threading

#kreirame socket
s = socket(AF_INET,SOCK_DGRAM) #udp socket
port = 7777
MAX = 65535 #maksimalna golemina na poraka sto moze da se isprati 

#kreirame klasa klient koja ke gi cuva podatocite na klientot
class KLient():

    #za inicijalizacija na nov klient
    def __init__(self, ime, prezime, username, password, adresa):
        self.ime = ime
        self.prezime = prezime
        self.username = username
        self.password = password
        self.adresa = adresa
        self.razgovori = {} #ovde ke se cuvaat razgovorite na self klientot so dr klienti 
        # razgovori = {"username1": ["poraka1", "poraka2", ..], "username2": [], ...}
        #ovoj del e vsunost konstruktor koga se kreira nov klient sto go zapisuva vo samat baza
        # self e pokazuvac kon konkreten objakt, na mesto na self se pisuva pr k1 za korisnik1

    #dodavanje na porakata vo istorija na razgovori, self ni e korisnikot, k e dr korisnik so koj komunicira
    def dodajPoraka(self, poraka, k):
        if k in self.razgovori:
            self.razgovori[k] += [poraka] #ako ima vekje razmenuvano poraki so klientot k, dodadi ja i novata poraka
        else:
            self.razgovori[k] = [] #ako nema, kreirame nov zapis
            self.razgovori[k] += [poraka] #i togas ja dodavame porakata

#ceka da stigne poraka
def klientCekaj(s):
    while True:
        data, addr = s.recvfrom(MAX) #prima poraka vo bytes - data i ip + port - addr
        print("Poraka:", data.decode()) #ja dekodira porakata od bytes vo string i ja prikazuva

if sys.argv[-1] == 'server':
    klienti = {}    #tuka ke gi zapisuva site klienti vo bazata, username:objektKlient(i tuka ke gi ima site podatoci sto gi zacuvuva gore)
    s.bind(('127.0.0.1', port)) #povrzuva so adresa i porta na koja ke slusa serverot
    print(f'Listening at {s.getsocketname()}')

    while True: 
        data, addr = s.recvfrom(MAX)
        data = pickle.loads(data) #gi pretvara podatocite od bytes vo objekt, recnik

        if data["registracija"] == 1: #ako porakata e za registracija, data["registracija"] e 1, a ako e poraka do drug klient, data["registracija"] e 0
            if data['username'] in klienti: #proverka dali vekje go ima ovoj username
                s.sendto('Korisnickoto ime e zafateno, probajte drugo.'.encode(), addr) #so encode poraka vo bytes
            else:
                #ako ne e zafateno, kreirame nov objekt Klient so podatocite od porakata i go zacuvuvame vo bazata
                klienti[data['username']] = KLient(
                    data['ime'], 
                    data['prezime'], 
                    data['username'], 
                    data['password'], 
                    addr) #go kreirame noviot objekt so site podatoci
                s.sendto('Uspeshna registracija!'.encode(), addr) #vrakja nazad poraka
        
        elif data["registracija"] == 0: #togas e normalna poraka do dr klient
            if[data['to']] in klienti: #dali go ima registirao korisnikot do koj treba da stigne porakata vo klienti

                for klient in klienti.values(): #tuka gi izminuvame site podatoci od objekotot so values
                    if klient.adresa == addr:
                        sender = klient.username
                        break #vekje go imame najdeno isprakjacot izleguvame od ovoj for
                
                s.sendto((sender + ":" + data['msg']).encode(), klienti[data['to']].adresa)
                #serverot ja isprakja porakata do adresata na primacot

                klienti[data['to']].dodajPoraka(data['msg'], sender) #ja dodava porakta kaj primacot

                s.sendto('Uspesno ispratena poraka!'.encode(), addr) # vrakja potvrda na isprakjacot
            else:
                s.sendto('Korisnikot ne e registriran. Obidi se povtorno!'.encode(), addr)

elif sys.argv[-1] == "client":
    ime = input('Vnesi ime:')
    prezime = input('Vnesi prezime:')

    while True:
        username = input('vnesi username:')
        password = input('vnesi password:')

        #kreirame recnik koj e poraka za registracija , site potrebni info za registracija
        msg = {"registracija":1, "ime":ime, "prezime":prezime, "username":username, "password":password}

        msg = pickle.dumps(msg) #transformira od objekt-dictionary vo bytes za da moze da ja prati  do serverit
        s.sendto(msg, ('127.0.0.1', port)) #ja isprakja porakata do serverot

        ans, _ = s.recvfrom(max) #ceka odg od serverot, 
        #ans e porakta sto odg serverot, _ e adresa od kade signala porakata sto vo ovoj slucaj ne ni treba

        print(ans.decode()) #od bytes vo text

        if(ans.decode() == 'Uspresna registracija'):
            break 
    
    threading.Thread(target=klientCekaj, args=(s,)).start() #kreirame nova nitka, ovaa nitka ovozmozuva postojano da slusa i ceka info 
    
    while True:
        #prakjanje poraka do dr klienti
        to = input('Do kogo pisuvas?')
        poraka = input('Vnesi poraka: ')

        msg = {"registracija":0, "to":to, "msg":poraka} #kreirame poraka za isprakjanje do dr klient, so potrebni info
        
        msg = pickle.dumps(msg) #od objekt-dictionary vo bytes
        s.sendto(msg, ('127.0.0.1', port)) #porakata ja isprakja do serverot

else:
    print(sys.stderr, 'ERRORa')
    sys.exit(-1)
