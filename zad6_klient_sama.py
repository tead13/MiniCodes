from socket import *  # Gi vnesuvame site potrebni socket funkcionalnosti za TCP komunikacija.
import xmlrpc.client as client  # Go vnesuvame XML-RPC klient modulot za povikuvanje funkcii na serverot.
import threading  # Go vnesuvame modulot threading za da mozheme paralelno da slushame poraki.
import struct  # Go vnesuvame struct za pakuvanje i raspakuvanje na dolzhina na poraka.

s = socket(AF_INET,SOCK_STREAM)  # Kreirame TCP socket shto ke sluzhi klientot da slusha za P2P poraki od drugi klienti.
proxy = client.ServerProxy('http://127.0.0.1:12345')  # Kreirame RPC proxy objekt preku koj ke gi povikuvame funkcijite od serverot.

def recv_all(sc, msg_len):  # Pomoshna funkcija shto cita tochno msg_len bajti od socket.
    data = b''  # Pocnuvame so prazen byte string.
    while len(data)< msg_len:  # Dodeka nemame procitano dovolno bajti.
        more = sc.recv(msg_len - len(data))  # Prima uste tolku bajti kolku shto falat.
        if not more:  # Ako ne se primi nishto, vrskata verojatno e prekinata.
            raise EOFError(f'read {len(data)} from {msg_len}B message.')  # Frla greshka deka ne e primena cela poraka.
        data += more  # Go dodava noviот del vo vekje procitanite podatoci.
    return data  # Ja vrakja celata procitana sodrzhina.

def slusaj(s):  # Funkcija shto postojano slusha za poraki od drugi klienti.
    s.listen(5)  # Go stava socketot vo pasiven rezim za slushanje na konekcii.
    while True:  # Beskonecna petlja za postojano prifakjanje poraki.
        sp2p, _ = s.accept()  # Prifakja nova konekcija od drug klient i dobiva nov socket za nea.
        poraka = recv_all(sp2p,struct.unpack("!i",recv_all(sp2p,4))[0]).decode()  # Prvo chita 4 bajti za dolzhina, ja pretvora vo int, pa ja chita celata poraka i ja dekodira vo string.
        print(poraka)  # Ja pecati primenata poraka na ekran.
        sp2p.close()  # Ja zatvora P2P konekcijata po primanjeto.

while True:  # Glavna beskonecna petlja so meni komandi.
    cmd = input("<<<\nRegistracija - r \n Najava - n \n Odjava - o \n Kreiraj grupa - kg \n Prikluci grupa - pg \n Isprati do korisnik - ik \n Isprati do grupa - ig\n>>>")  # Go bara izborot od korisnikot.
    if cmd == 'r':  # Ako korisnikot odbral registracija.
        korime = input("Vnesi username: ")  # Bara korisnicko ime.
        lozinka = input("Vnesi password: ")  # Bara lozinka.
        print(proxy.registracija(korime,lozinka))  # Ja povikuva RPC funkcijata registracija na serverot i go pecati odgovorot.

    if cmd == 'n':  # Ako korisnikot odbral najava.
        korime = input("Vnesi username: ")  # Bara korisnicko ime.
        lozinka = input("Vnesi passowrd: ")  # Bara lozinka.
        s.bind(('127.0.0.1',0))  # Go vrzuva socketot na lokalna adresa i slobodna porta shto sistemot sam ja izbirа.
        print(s.getsockname())  # Ja pechati adresata i portata na koi klientot ke slusha poraki.
        threading.Thread(target=slusaj,args=(s,)).start()  # Startuva posebna nitka shto ke slusha incoming poraki.
        print(proxy.najava(korime,lozinka,s.getsockname()[0],s.getsockname()[1]))  # Mu gi prakja na serverot username, lozinka, IP i porta za najava.

    if cmd == 'o':  # Ako korisnikot odbral odjava.
        print(proxy.odjava(korime))  # Ja povikuva RPC funkcijata odjava za tekovniot korisnik.
    
    if cmd == 'kg':  # Ako korisnikot odbral kreiranje grupa.
        ime = input("Vnesi ime na grupata: ")  # Bara ime na novata grupa.
        print(proxy.kreiraj_grupa(ime))  # Ja povikuva RPC funkcijata za kreiranje grupa.

    if cmd == 'pg':  # Ako korisnikot odbral priklucuvanje vo grupa.
        ime = input("Vnesi ime na grupata kade sakas da se priklucis: ")  # Bara ime na grupata.
        print(proxy.prikluci_grupa(ime,korime))  # Ja povikuva RPC funkcijata za priklucuvanje vo grupata.

    if cmd == 'ik':  # Ako korisnikot saka da prati poraka do eden korisnik.
        dokogo = input("Vnesi uname do kogo ke prakas: ")  # Bara korisnicko ime na primachot.
        if proxy.prati_korisnik(korime,dokogo) != "Ne ste najaveni ili korisnikot do koj sakate da pratite ne e najavi.":  # Proveruva dali serverot vratil adresa/porta namesto poraka za greshka.
            addr, port = proxy.prati_korisnik(korime, dokogo)  # Ja zema adresata i portata na primachot od serverot.
            sp = socket(AF_INET, SOCK_STREAM)  # Kreira nov TCP socket za ovaa konkretna poraka.
            sp.connect((addr,port))  # Se povrzuva direktno so klientot-primach.
            poraka = input("Vnesi poraka: ")  # Go bara tekstot na porakata.
            msg = ("\n"+korime+ ": " + poraka).encode()  # Ja formira porakata kako bytes vo format "korime: poraka".
            sp.sendall(struct.pack("!i",len(msg))+msg)  # Prvo ja prakja dolzhinata na porakata vo 4 bajti, pa posle samata poraka.
            sp.close()  # Ja zatvora konekcijata po isprakjanjeto.
        else:  # Ako serverot vratil poraka za greshka.
            print(proxy.prati_korisnik(korime, dokogo))  # Ja pecati porakata za greshka.
        
    if cmd == 'ig':  # Ako korisnikot saka da prati poraka do grupa.
        dokoja= input("ime na grupa: ")  # Bara ime na grupata.
        clenovi = proxy.isprati_grupa(korime, dokoja)  # Od serverot gi bara clenovite od grupata.
        print(type(clenovi))  # Go pecati tipot na vrateniot odgovor, verojatno za proverka.
        poraka = input("Vnesi poraka: ")  # Go bara tekstot na grupnata poraka.
        msg = ("grupa \'"+dokoja+"\' | "+korime+ ": " + poraka).encode()  # Ja formira porakata so ime na grupa, isprakjach i tekst, pa ja pretvora vo bytes.
        full_msg = struct.pack("!i",len(msg))+msg  # Ja pakira porakata: prvo 4 bajti dolzhina, pa samata sodrzhina.

        for clen in clenovi:  # Pominuva niz site clenovi od grupata.
            addr, porta = clenovi[clen]  # Ja zema adresata i portata na tekovniot clen.
            if addr == s.getsockname()[0] and int(porta) == s.getsockname()[1]:  # Proveruva dali tekovniot clen e samiot isprakjach.
                continue  # Ako e samiot sebe, go preskoknuva za da ne si ja prati porakata sam na sebe.
            spc = socket(AF_INET,SOCK_STREAM)  # Kreira nov TCP socket za toj konkreten clen.
            spc.connect((addr,int(porta)))  # Se povrzuva direktno so toj clen.
            spc.sendall(full_msg)  # Ja isprakja porakata.
            spc.close()  # Ja zatvora konekcijata.