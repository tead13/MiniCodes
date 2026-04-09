#Да се напише програма во која клиенти можат да комуницираат меѓу себе со помош на
#серверот. Клиентите се регистрираат на серверот. Откако ќе бидат регистрирани можат да
#праќаат порака до други клиенти. Притоа, истовремено треба да можат да примаат и
#пораки од други клиенти.

from socket import *
import threading, struct #threading za da moze serverot da raboti so povekje klienti istovremeno 
                         #struct za da moze da pakuva i otpakuva pakrti vo bytes

s = socket(AF_INET, SOCK_STREAM) # tcp socket
# AF_INET - IPv4, SOCK_STREAM - TCP

klienti = {} # dictionary kaj ke gi cuva klientite -> username:socket
l = threading.Lock() #????

#funkcija koja prima sc-socket i broj msg_len - dolzina na porakata, mora vaka bidejkji samo so recvfrom vo tcp se dobivaat segmetni od porakata
def recv_all(sc, msg_len):
    data = b'' #definirame prazen string, vo bytes
    while len(data)< msg_len: #dodeka ne stigne celata poraka, bidejkji TCP e stream protokol i moze da se desi da stigne del od porakata, a del da se izgubi
        more = sc.recv(msg_len - len(data)) #more e uste kolku bajti ni falat da dobieme od adr
        if not more: #me buni uslovot
            #fela greska deka ne e primena celosna poraka
            raise EOFError(f'read {len(data)} from {msg_len}B message.') #?raise ne go razbiram bas
        data += more
    return data

#funkcija kora raboti so eden konkreten klient, prima socket na klientot
def opsluziKlient(sc):
    # registracija i preprakanje na poraki
    while True:
        dolzina = struct.unpack("!i",recv_all(sc,4))[0] #gi cita prvite 4 bytes od porakata i so niv kazuva kolku e dolga prakata
        poraka = recv_all(sc,dolzina).decode().split('|') #ja cita celata poraka, ja pretvora vo string i aj deli spored | pr."registracija|ana" treba da gi oddeli 
        if poraka[0] == 'registracija': # registracija|korisnik_sc
            korisnik_sc = poraka[1]    
            l.acquire() #???? kako fukcionira so lock
            try:
                if korisnik_sc in klienti:
                    msg = 'Neuspeshno!'.encode() #ako vekje postoi korisnickoto ime, neuspesna registracija
                    dolz = struct.pack("!i",len(msg)) #sepakuva dolzinata na porakata
                    sc.sendall(dolz+msg)  #se prakja dolzinata + porakata do klientot
                else:
                    klienti[korisnik_sc] = sc #se kreira nov korisnik 
                    msg = 'uspesna registracija'.encode() #istoto go pravi samo so uspesna reg 
                    dolz = struct.pack("!i", len(msg))
                    sc.sendall(dolz+msg)
            finally:
                l.release() #??? prestanuva lock 
        elif poraka[0] == 'porakado' and poraka[1] in klienti:#porakado|korisnik_do|poraka|korisnik_sc
            dest = poraka[1] #klient dokogo se isprakja
            msg = poraka[3] +': '+poraka[2] # imeto na isprakjacot: porakata
            length = struct.pack("!i",len(msg.encode())) #se pakuva dolzinata
            full_msg = length+msg.encode() #dozinata so spakuvanata poraka se prakja
            klienti[dest].sendall(full_msg) # klienti[dest] e socket

s.bind(('127.0.0.1', 7777))
s.listen() #listening mode
print('Server listening..')

while True:
    sc, addr = s.accept() #ceka da se povrze nekoj klient ?
    threading.Thread(target=opsluziKlient, args=(sc,)).start()
    #kreira nov sto ke izvrsuva funk opsluziKlient za dadeniot klient