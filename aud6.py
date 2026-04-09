# Да се напише дистрибуирана P2P клиент сервер апликација со употреба на TCP и RPC.
# Клиентот треба да се регистрира на серверот со единствено корисничко име и лозинка. По
# успешна регистрација клиентот треба да се најави на серверот. Најавените клиенти можат
# да праќаат пораки до други најавени клиенти. Секој најавен клиент може да креира група
# со одредено име ако таа група не постои, да се приклучи на одредена група ако веќе не е
# член и да испраќа пораки до групата во која што е член. Клиентот треба да има можност и
# да се одјави од серверот. Притоа, регистрацијата, најавата, одјавата, креирањето на група се
# контролна комуникација со северот, додека праќањето на порака од клиент до друг клиент
# или група е податочна комуникација.

from xmlrpc.server import SimpleXMLRPCServer

class korisnik():
    def __init__(self,korime,lozinka, najaven=0, adresa ='', porta = 0):
        self.korime = korime
        self.lozinka =lozinka
        self.najaven = najaven
        self.adresa = adresa
        self.porta = porta
#?zs vaka
class grupa():
    def __init__(self, ime):
        self.ime = ime
        self.clenovi = {}

korisnici = {}
grupi = {} # {"Grupa1": (ime:grupa1, clenovi:{ime:clen1,....})}

def registracija(korime, lozinka):
    if korime in korisnici:
        return "Korisnickoto ime e zafateno."
    else:
        korisnici[korime] = korisnik(korime, lozinka)
        return "Uspeshna registracija."

def najava(korime, lozinka, ipaddr, port):
    if korime in korisnici and korisnici[korime].lozinka == lozinka:
        korisnici[korime].adresa = ipaddr
        korisnici[korime].porta = port
        korisnici[korime].najaven = 1

        return "Uspeshna najava."
    else:
        return "Greshna lozinka ili korisnicko ime."


def odjava(korime):
    if korime in korisnici and korisnici[korime].najaven == 1:
        korisnici[korime].najaven = 0
        for grupa in grupi:
            if korime not in grupa.clenovi:
                del grupa.clenovi[korime]
        return "Uspeshno se odjavivte."
    else:
        return "Greshka pri odjavuvanje."

def kreiraj_grupa(ime):
    if ime in grupi:
        return "Veke postoi grupa so takvo ime."
    else:
        grupi[ime] = grupa(ime)
        return "Uspeshno kreirana grupa!"

def prikluci_grupa(ime,korime):
    if korime in korisnici and korisnici[korime].najaven == 1:
        if ime in grupi and korime not in grupi[ime].clenovi:
            grupi[ime].clenovi[korime] = (korisnici[korime].adresa, korisnici[korime].porta)

            return "Uspehsno se priklucivte na grupata."
        else:
            return "Ne postoi takva grupa./Veke ste clen na grupata."
    else:
        return "Ne ste najaveni."

def prati_korisnik(korime, korime_prati):
    if korime not in korisnici and korime_prati not in korisnici:
        return "Ne ste registrirani ili korisnikot do koj sakate da pratite ne e registriran."
    if korisnici[korime].najaven == 1 and korisnici[korime_prati].najaven == 1:
        return korisnici[korime_prati].adresa, korisnici[korime_prati].porta
    else:
        return "Ne ste najaveni ili korisnikot do koj sakate da pratite ne e najavi."

def isprati_grupa(korime, ime):
    if korime not in korisnici:
        return "Ne ste registrirani."
    if korisnici[korime].najaven:
        print(type(grupi[ime].clenovi))
        print(grupi[ime].clenovi)
        return grupi[ime].clenovi
    
#?dali ovdeka gi povikuva funkc
server = SimpleXMLRPCServer(('127.0.0.1',12345))
server.register_function(najava)
server.register_function(registracija)
server.register_function(prati_korisnik)
server.register_function(isprati_grupa)
server.register_function(odjava)
server.register_function(kreiraj_grupa)
server.register_function(prikluci_grupa)

print("Server up and listening..")
server.serve_forever()
