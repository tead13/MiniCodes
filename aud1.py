# Да се напише едноставна UDP клиент-сервер апликација во која серверот ќе чека 
# пораки од клиенти, а клиентот ќе испраќа порака и ќе чека потврден одговор за 
# прием од серверот.

import socket, sys

PORT = 7777 #porta na koj ke  komuniciraat serverot i klientot
MAX =65535 #maksimalna golemina na poraka

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp socket 
'''AF_NET = IPv4, SOCK_DGRAM = UDP'''

# server
if sys.argv[-1] == 'server': #proveruva dali posleniot element od nizata e server
    s.bind(('127.0.0.1',PORT))
    print(f'Listening at: {s.getsockname()}')

    while True:
        data, addr = s.recvfrom(MAX) #data e vo bytes, addr e tuple od ip adresa i port
        print(f'The client says {data.decode()}')
        s.sendto(f'Your message was {len(data)} bytes'.encode(), addr) #ja enkodiraporakata vo bytes i ja prakja do adresata addr vo oblik bytes


# client
elif sys.argv[-1] == 'client':
    print(f'Before sending {s.getsockname()}')
    msg = input('Enter msg to be sent to server:')
    s.sendto(msg.encode(), ('127.0.0.1',PORT))
    print(f'After sending msg {s.getsockname()}')
    data, addr = s.recvfrom(MAX)
    print(f'Server says: {data.decode()}')

else:
    print("Nepravilen povik na skriptata")
    sys.exit(-1)


# Bitna sintaksa
# s.recvfrom(MAX) - prima poraka od klientot i vrakja podatoci i adresa znaci zapisuva poraka vo data i vo addr ip adresa i porta na klientot
# data.decode() - gi pretvora podatocite od bytes vo tekst
# s.sendto("msg", addr) - ispraka poraka msg do klientot na adresa addr
# s.getsockname() - vrakja tuple od ip adresa i port na koj e vezan socketot
# msg.encode() - gi pretvora podatocite od tekst vo bytes

'''
bitno e deka cela komunikacija se odviva vo bytes, i treba da se enkodira i dekodira porakata za da se pretvori od tekst vo bytes i obratno
bez razlika dali e server ili klient, 
prvin treba da se povrze na adresa i port, potoa se isprakja poraka i se ceka odgovor od drugata strana, i se prikazuva porakata od drugata strana
bidejkji udp e brza no ne tolku sigurna komunikacija moze da imame zaguba na poraka
'''