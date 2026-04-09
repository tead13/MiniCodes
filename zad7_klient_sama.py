import xmlrpc.client as client  # Go vnesuvame XML-RPC klient modulot za povikuvanje funkcii na serverot.
from socket import *  # Gi vnesuvame socket alatkite za TCP komunikacija megju klientite.
import struct, pickle, threading  # struct za pakuvanje dolzina na poraka, pickle e importiran ama ovde realno ne se koristi, threading za paralelno slushanje.

def recv_all(sc, msg_len):  # Pomoshna funkcija shto treba da procita tochno msg_len bajti od socket.
    data = b''  # Pocnuvame so prazen byte-string.
    while len(data)< msg_len:  # Dodeka ne ja procitame celata poraka.
        more = sc.recv(msg_len - len(data))  # Prima uste tolku bajti kolku shto falat.
        if not more:  # Ako ne stigna nishto, konekcijata verojatno e prekinata.
            raise EOFError(f'read {len(data)} from {msg_len}B message.')  # Frla greshka deka ne e procitana cela poraka.
        data += more  # Go dodava novoprocitaniot del vo data.
    return data  # Ja vrakja celata procitana sodrzhina.

def slusaj(s):  # Funkcija shto postojano slusha za TCP poraki od drugi klienti.
    s.listen(5)  # Go stava socketot vo pasiven rezim za slushanje na konekcii.
    while True:  # Beskonecno chekanje na novi konekcii.
        sp2p, _ = s.accept()  # Prifakja nova konekcija od drug klient i vrakja nov socket za nea.
        poraka = recv_all(sp2p,struct.unpack("!i",recv_all(sp2p,4))[0]).decode()  # Prvo chita 4 bajti dolzhina, gi pretvora vo int, pa ja chita cela poraka i ja dekodira vo string.
        print(poraka)  # Ja pecati primenata poraka.
        sp2p.close()  # Ja zatvora konkretnata P2P konekcija.

proxy = client.ServerProxy('http://127.0.0.1:12345')  # Kreira RPC proxy objekt preku koj ke se povikuvaat funkcijite na serverot.

najaven_vo_sesija = 0  # Lokalno flagche dali korisnikot e najaven vo momentalnata klientska sesija.

while True:  # Glavna meni-petlja na klientot.
    cmd = input("<<<\nRegistracija - r \n Najava - n \n Odjava - o \n Kreiraj grupa - kg\
                 \n Prikluci grupa - pg \n Isprati do korisnik - ik \n Isprati do grupa - ig \
                \n Prati trud - pt \n Vidi trudovi - vt \n Napushti grupa - ng \n Odjava - o\n>>>")  # Go bara izborot od korisnikot.

    if cmd == 'r':  # Ako korisnikot odbral registracija.
        ime = input("Vnesi ime: ")  # Bara ime.
        korime = input('Vnesi username: ')  # Bara korisnicko ime.
        pasvord = input("Vnesi pass: ")  # Bara lozinka.
        pozicija = input("Vnesi pozicija: ")  # Bara pozicija.
        print(proxy.registracija(pozicija, ime, korime, pasvord))  # Ja povikuva serverската RPC funkcija za registracija i go pecati odgovorot.

    if cmd == 'n':  # Ako korisnikot odbral najava.
        if najaven_vo_sesija:  # Ako vekje e najaven vo ovaa sesija.
            print('Najaveni ste.')  # Pecati poraka deka vekje e najaven.
        else:  # Ako ne e najaven.
            korime = input("Vnesi username: ")  # Bara korisnicko ime.
            pasvord = input("Vnesi passowrd: ")  # Bara lozinka.
            s = socket(AF_INET, SOCK_STREAM)  # Kreira TCP socket na klientska strana za primanje P2P poraki.
            s.bind(('127.0.0.1',0))  # Go vrzuva socketot na lokalna adresa i slobodna porta shto sistemot sam ke ja izbere.
            print(s.getsockname())  # Ja pecati lokalnata adresa i porta na klientot.
            threading.Thread(target=slusaj,args=(s,)).start()  # Startuva posebna nitka shto postojano ke slusha incoming P2P poraki.
            odgovor = proxy.najava(korime,pasvord,s.getsockname()[0],s.getsockname()[1])  # Mu gi prakja na serverot username, lozinka, IP adresa i porta za da gi zapamti.
            print(odgovor)  # Go pecati odgovorot od serverot.
            if odgovor == "Uspeshno se najavivte.":  # Ako najavata e uspesna.
                najaven_vo_sesija = 1  # Go menuvame lokalniot flag vo najaven.

    if cmd == 'kg':  # Ako e odbrano kreiranje grupa.
        ime = input("Vnesi ime na grupata sto ja kreirash: ")  # Bara ime na nova grupa.
        print(proxy.kreiraj_grupa(korime,ime))  # Povikuva RPC funkcija za kreiranje grupa.

    if cmd == 'pg':  # Ako e odbrano priklucuvanje vo grupa.
        ime = input("Vnesi ime na grupata kade sakas da se priklucis: ")  # Bara ime na grupa.
        print(proxy.prikluci_grupa(korime,ime))  # Povikuva RPC funkcija za priklucuvanje vo grupa.

    if cmd == 'bg':  # Ako e odbrano brishenje grupa.
        ime = input("Vnesi ime na grupata koja sakas da ja izbrishesh: ")  # Bara ime na grupata shto treba da se izbrishe.
        print(proxy.kreiraj_grupa(korime,ime))  # OVA E GRESHKA: treba da bide proxy.brishi_grupa(korime, ime), ne kreiraj_grupa.

    if cmd == 'ik':  # Ako e odbrano isprakjanje do eden korisnik.
        dokogo = input("Vnesi dokogo: ")  # Bara korisnicko ime na primachot.
        if isinstance(proxy.isprati_korisnik(korime, dokogo),str):  # Ako funkcijata vratila string, toa znachi deka vratila poraka za greshka.
            print(proxy.isprati_korisnik(korime, dokogo))  # Ja pecati greshkata.
        else:  # Ako ne vratila string, znachi vratila adresa i porta.
            addr, porta = proxy.isprati_korisnik(korime, dokogo)  # Gi zemame adresata i portata na primachot.

            sp2p = socket(AF_INET,SOCK_STREAM)  # Kreira nov TCP socket za ovaa konkretna P2P poraka.
            sp2p.connect((addr,porta))  # Se povrzuva direktno do klientot-primach.
            poraka = input("Vnesi poraka: ")  # Go bara tekstot na porakata.
            full_msg = struct.pack("!i",len(poraka.encode()))+poraka.encode()  # Ja pakira porakata: prvo 4 bajti za dolzhina, pa samata poraka vo bytes.
            sp2p.send(full_msg)  # Ja isprakja porakata do primachot.
            sp2p.close()  # Ja zatvora konekcijata po isprakjanjeto.
    
    if cmd == 'ig':  # Ako e odbrano isprakjanje do grupa.
        ime = input("Do koja grupa? ")  # Bara ime na grupata.
        clenovi = proxy.isprati_grupa(korime, ime)  # Od serverot gi bara clenovite na grupata i nivnite adresi.
        if isinstance(clenovi,str):  # Ako e vraten string, toa e greshka ili poraka.
            print(clenovi)  # Ja pecati porakata.
        else:  # Ako e vraten rechnik so clenovi.
            poraka = input("Vnesi poraka: ")  # Go bara tekstot na porakata.
            full_msg = struct.pack("!i",len(poraka.encode()))+poraka.encode()  # Ja pakira porakata vo format dolzhina + sodrzhina.
            for clen in clenovi:  # Pominuva niz site clenovi od grupata.
                addr, porta = clenovi[clen]  # Ja zema adresata i portata na tekovniot clen.
                sg = socket(AF_INET,SOCK_STREAM)  # Kreira nov TCP socket za toj clen.
                sg.connect((addr,porta))  # Se povrzuva so toj clen.
                sg.send(full_msg)  # Ja isprakja istata poraka i do toj clen.
                sg.close()  # Ja zatvora konekcijata.

    if cmd == 'pt':  # Ako e odbrano prakjanje trud.
        naslov = input("Vnesi naslov na trudot")  # Bara naslov na trudot.
        link = input("Vnesi go linkot")  # Bara link do trudot.
        print(proxy.prati_trud(korime,naslov,link))  # Povikuva RPC funkcija za dodavanje trud na serverot.

    if cmd == 'vt':  # Ako e odbrano gledanje trudovi.
        trudovi = proxy.vidi_trudovi(korime)  # Go bara rechnikot so trudovi od serverot.
        if isinstance(trudovi,dict):  # Ako odgovorot e rechnik, znachi uspesno se vrateni trudovite.
            for trud in trudovi:  # Pominuva niz site trudovi.
                print(f"{trud}: {trudovi[trud]}")  # Gi pecati vo forma naslov : link.
        else:  # Ako ne e rechnik, odgovorot e poraka za greshka.
            print(trudovi)  # Ja pecati porakata.

    if cmd == 'ng':  # Ako e odbrano napushtanje grupa.
        ime_grupa = input('Od koja grupa sakate da izlezete? ')  # Bara ime na grupata od koja korisnikot saka da izleze.
        print(proxy.napusti_grupa(ime_grupa, korime))  # Povikuva RPC funkcija za napushtanje grupa.

    if cmd == 'o':  # Ako e odbrana odjava.
        print(proxy.odjava(korime))  # Povikuva RPC funkcija za odjava na korisnikot.
        najaven_vo_sesija = 0  # Lokalno go resetira flagot za sesija.