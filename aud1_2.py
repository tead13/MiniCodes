#ista zadaca kako zad1 samo so gubenje na paketi, t.e da ceka odredeno vreme i ako nema odg go smeta za izguben


from socket import *
import sys, random

s = socket(AF_INET, SOCK_DGRAM)
MAX = 65535

if sys.argv[-1] == 'server':
    s.bind(('127.0.0.1', 12345)) #slusa samo na ovaa adresa
    print(f'Listening at: {s.getsockname()}') #da ja prikaze adr na koja slusa

    while True: #bidejkji postojano ceka poraka od klienti, beskonecna jamka
        data, addr = s.recvfrom(MAX) #prima poraka od klient, data e vo bytes, addr e tuple od ip adresa i port
        
        if random.randint(0,1): # simulirame dali ke se izgubi porakata ili ne
            print(f'The client says: {data.decode()}') #ja dekodira od bytes vo string
            s.sendto(f'Your msg was {len(data)} bytes'.encode(), addr) #isprakja nazad do klientot poraka, ja enkodira od string vo bytes i ja prakja do adresata addr
        else:
            print('Packet dropped.') #ako e 0 

elif sys.argv[-1] == 'client':
    s.connect(('127.0.0.1', 12345)) #vaka ke pamti so koj server ke komunicira, port i adresa

    delay = 0.5 #vreme sto ke ja poceka porakata
    while True:
        msg = input() #korisnikot ja pisuva porakata - text
        s.send(msg.encode()) #vnesenata poraka ja enkodira vo bytes i ja isprakja do serverot

        #cekanje odg
        s.settimeout(delay) #ako go nadmine vremeto za cekanje, dava socket.timeout red36

        try: #vo try e kod sto moze da frli greska, no sepak probuvame mozno e id a de e uspesen, vo ovoj slucaj dali e primena porakata
            data = s.recv(MAX) #ja prima porakta od serverot, nema adr, fiksna e vekje ja znae
        except socket.timeout: #ocekuvano e da se javi greska i odi na sledno e toa deka ocekuva da postoi nekoj timeout
            delay *= 2 # se zgolemuva delay i se vrakja nazad vo while
            if delay > 1.0: #tuka definirame kolku vreme ke ceka da stigne porakata
                raise RuntimeError('The packet is being dropped') # ako ima timeout paketot e izguben 
        except:
            raise #ako ima bilo koja dr greska a ne e timeout, kraj na programata
        else:
            break #ako uspesno e primena porakata izleguva od while loop

    print(f'Server says {data.decode()}') #ako se e uspesno, porakata ja dekodira


else:
    print(sys.stderr,'nepravilen povik')

# Bitna sintaksa
# s.bind() - go povrzuva soketot na adresa i port za da slusa, najcesto se koristi za serverot 
# s.connect() - ne pravi vistinska konekcija kako pri tcp, samo mu kazuva na soketot ke komuniciram so ovoj server
# random.randomint(0,1) - vrakja random broj 0 ili 1, se koristi za da se odlucuva dali ke se ispraka porakata ili ke se smeta za izgubena
# s.settimeout(delay) - postavuvame vremensko ogranicuvanje za cekanje na odgovor od serverot, ako ne dojde odgovor vo toa vreme se frla socket.timeout

'''
1. nacin bez connect:
    se korisiti sendto() i recvfrom() i se navreduva adresa i port pri isprakjanje poraka, i se ceka odgovor od serverot so recvfrom()
    sekoj pat koga se prakja poraka mora da se navede od kade doadja porakata
    s.sendto(data, ('127.0.0.1', 12345))
    koga se prima poraka, zaedno so porakata se dobiva i adresa od kade e ispratena
    data, addr =s.recvfrom(MAX) - vrakja tuple od poraka i adresa od kade e ispratena porakata
    moze da se raboti so povekje adresi vo eden kod 
    
2. nacin so connect:
    se koristi connect() za da se navede so koj server ke komunicirame, i potoa se koristi send() i recv() bez da se navreduva adresa i port
    se raboti so edna fiksna adresa i e poednostavno 
    s.connect(('127.0.0.1', 12345))  - ednas se definira adresata i portata i celo vreme komunikacijata medju serverot i klientot odi so taa adresa i port
    s.send(data) - isprakja poraka do serverot
    data = s.recv(MAX) - prima poraka od serverot

'''