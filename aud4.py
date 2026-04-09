from socket import *
import threading, struct, pickle

s = socket(AF_INET, SOCK_STREAM)
PORT = 12345

biblioteka = {}
l = threading.Lock()

def recv_all(sc, msg_len):
    data = b''
    while len(data)< msg_len:
        more = sc.recv(msg_len - len(data))
        if not more:
            raise EOFError(f'read {len(data)} from {msg_len}B message.')
        data += more
    return data

def opsluziKlient(sc):
    while True:
        length = struct.unpack("!i",recv_all(sc,4))[0]
        data = recv_all(sc, length)
        data = data.decode().split("|")
        if data[0] == 'konekcija': # konekcija|adresa|porta
            msg = 'OK Prati lista!'.encode()
            full_msg = struct.pack("!i",len(msg))+msg
            sc.sendall(full_msg)
            dolzina = struct.unpack("!i",recv_all(sc,4))[0]
            naslovi_od_klient = pickle.loads(recv_all(sc,dolzina))
            print(f'Klientot so adresa {data[1]}:{data[2]} gi cuva statiite:')
            with l:
                for naslov in naslovi_od_klient:
                    biblioteka[naslov] = (data[1],data[2])
                    print(f' {naslov}')
            odgovor = 'Uspeshno vneseni naslovi!'.encode()
            sc.sendall(struct.pack("!i",len(odgovor))+odgovor)
        elif data[0] == 'prebaruvanje': # prebaruvanje|naslov
            with l:
                if data[1] in biblioteka:
                    odgovor = 'OK|'+ biblioteka[data[1]][0] + "|" + biblioteka[data[1]][1]
                    sc.sendall(struct.pack("!i",len(odgovor.encode()))+odgovor.encode())
                else:
                    odgovor = 'Greska|Nema takva statija.'
                    sc.sendall(struct.pack("!i",len(odgovor.encode()))+odgovor.encode())

s.bind(('127.0.0.1',PORT))
s.listen(5)
print('Server listening..')

while True:
    sc, addr = s.accept()
    threading.Thread(target=opsluziKlient, args=(sc,)).start()
