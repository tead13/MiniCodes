from socket import *
import struct,sys, threading

s = socket(AF_INET, SOCK_STREAM) # Kreirame TCP socket so koj klientot ke se povrze so serverot.

def recv_all(sc, msg_len):
    data = b'' # Pocnuvame so prazen byte-string.
    while len(data)< msg_len: # Dodeka ne gi procitame site msg_len bajti.
        more = sc.recv(msg_len - len(data)) # Prima uste tolku bajti kolku shto falat.
        if not more: # Ako ne stigne nishto, vrskata e prekinata ili zatvorena.
            raise EOFError(f'read {len(data)} from {msg_len}B message.') # Frla greshka deka ne e procitana cela poraka.
        data += more # Go dodava noviot del vo data.
    return data # Ja vrakja celata primena sodrzhina.

def cekaj(s):
    while True:
        length = struct.unpack("!i",recv_all(s,4))[0] # Prvo cita 4 bajti sto ja pretstavuvaat dolzinata na slednata poraka.
        data = recv_all(s,length).decode() # Ja cita celata poraka spored taa dolzina i ja pretvora vo string.
        print(data) # Ja pecati primenata poraka na ekran.

s.connect(('127.0.0.1', 7777)) # Go povrzuva klientot so serverot na lokalna adresa i porta 7777.

username = input('Vnesete korisnicko ime: ') # Bara korisnicko ime od korisnikot.
msg = "registracija|"+username # Ja formira registraciskata poraka vo dogovoreniot format.
msg_encoded = msg.encode() # Ja pretvora porakata vo bytes.
length = len(msg_encoded) # Ja presmetuva dolzinata na porakata vo bajti.
full_msg = struct.pack("!i",length) + msg_encoded # Prvo ja pakuva dolzinata vo 4 bajti, pa ja dodava samata poraka.

s.sendall(full_msg) # Ja isprakja celata registraciska poraka do serverot.

dolzina = recv_all(s,4) # Prima 4 bajti odgovor od serverot shto ja oznachuvaat dolzinata na povratnata poraka.
dolzina = struct.unpack("!i",dolzina)[0] # Gi raspakuva tie 4 bajti vo integer.
ans = recv_all(s,dolzina) # Ja cita celata povratna poraka od serverot.

ans = ans.decode() # Ja pretvora povratnata poraka od bytes vo string.

if ans == "Neuspeshno!":
    print('Neuspeshna registracija!') # Pecati deka registracijata ne uspela.
    sys.exit(-1) # Ja prekinuva programata so kod za greska.
else:
    print('Uspeshna regstracija!') # Pecati deka registracijata e uspeshna.
    try:
        t = threading.Thread(target=cekaj, args=(s,)) # Kreira posebna nitka shto postojano ke slusha poraki od serverot.
        t.start() # Ja startuva nitkata za primanje poraki.
        while True:
            dokogo = input('Vnesi username na primac! ') # Bara korisnicko ime na primachot.
            poraka = input('Vnesi poraka: ') # Bara tekst na porakata.
            msg = 'porakado|'+dokogo+'|'+poraka+"|"+username # Ja formira porakata vo format: komanda|primach|tekst|isprakjach.
            msg = msg.encode() # Ja pretvora porakata vo bytes.
            dolz = struct.pack("!i",len(msg)) # Ja pakuva dolzinata na porakata vo 4 bajti.

            fullmsg = dolz+msg # Go sostavuva finalniot paket: dolzhina + poraka.
            s.sendall(fullmsg) # Ja isprakja porakata do serverot.
    except:
        print('Nekoja greshka..') # Pecati opsta poraka za greshka ako se sluchi iskluchok.
        sys.exit(-1) # Ja prekinuva programata.