# Да се направи мрежна апликација која би служела за организација на една конференција. 
# Апликацијата да биде дистрибуирана P2P клиент сервер апликација со употреба на TCP и RPC. 
# Секој корисник (клиент) најпрво треба да се регистрира и при регистрација да ја наведе 
# својата позиција (автор, организатор, администратор), име, корисничко име и лозинка. 
# За да можат регистрираните корисници да комуницираат меѓусебно, потребно е прво да бидат 
# најавени на серверот со корисничко име и лозинка.
# - Авторите можат да праќаат трудови до серверот (наслов на трудот и линк), да членуваат во 
# групи креирани од организаторите и да разменуваат пораки со кој било корисник.
# - Организаторите можат да креираат групи составени од автори на еден труд кој го ревидираат, 
# каде името на групата би бил насловот на трудот. Можат да членуваат во групи креирани од 
# менаџерот и да излегуваат од истите, и можат да разменуваат пораки со кој било корисник. 
# Дополнително организаторите имаат пристап до сите приложени трудови кои се зачувани на 
# серверот.
# - Менаџерот може да креира групи составени од организатори со име на задачата (пример: 
# сместување, пријавување, финансии..) и да ги брише истите. Може да разменува пораки со 
# било кој корисник.
# Секој корисник може сам да се одјави од серверот. Притоа, регистрацијата, најавата, 
# одјавата, креирањето и напуштањето на група се контролна комуникација со северот, додека 
# праќањето на порака од клиент до друг клиент или група е податочна комуникација.

#kolokviumska
from xmlrpc.server import SimpleXMLRPCServer

class korisnik():
    def __init__(self, pozicija, ime, korime,lozinka, najaven=0, adresa ='', porta = 0):
        self.pozicija = pozicija
        self.ime = ime
        self.korime = korime
        self.lozinka =lozinka
        self.najaven = najaven
        self.adresa = adresa
        self.porta = porta

class grupa():
    def __init__(self, ime, admin =''):
        self.ime = ime
        self.admin = admin
        self.clenovi = {}

korisnici = {}
grupi = {}
trudovi = {}

def registracija(pozicija, ime, korime, lozinka):
    if korime not in korisnici:
        korisnici[korime] = korisnik(pozicija, ime, korime, lozinka)
        return "Uspeshno se registriravte!"
    else:
        return "Veke ste registrirani.."
    
def najava(korime, lozinka, adresa, porta):
    if korime in korisnici:
        if korisnici[korime].najaven:
            return "Veke ste najaveni!"
        elif korisnici[korime].lozinka == lozinka:
            korisnici[korime].najaven = 1
            korisnici[korime].adresa = adresa
            korisnici[korime].porta = porta
            return "Uspeshno se najavivte."
        else:
            return "Greshna lozinka."
    else:
        return "Ne ste registrirani so toa korisnicko ime."

def prati_trud(korime, naslov, link):
    if korime in korisnici and korisnici[korime].najaven:
        if korisnici[korime].pozicija == "avtor":
            if naslov not in trudovi:
                trudovi[naslov] = link
                return "Uspesno dodaden trud."
            else:
                return "Veke ima takov trud."
        else:
            return "Nemate privilegii na avtor."
    else:
        return "Ne ste najaveni."

def kreiraj_grupa(korime,ime):
    if korime in korisnici and korisnici[korime].najaven:
        if korisnici[korime].pozicija == 'organizator' or korisnici[korime].pozicija == 'menadzer':
            if ime in grupi:
                return "Grupata postoi."
            else:
                grupi[ime] = grupa(ime) # {'korime': (addr,porta), ..}
                grupi[ime].admin = korime
                return "Uspesno kreiravte grupa"
        else:
            return "Nemate privilegii"
    else:
        return "Ne ste najaveni."
    
def prikluci_grupa(korime, ime):
    if korime in korisnici and korisnici[korime].najaven:
        if korisnici[korime].pozicija == 'avtor':
            if ime in grupi and korisnici[grupi[ime].admin].pozicija == 'organizator':
                grupi[ime].clenovi[korime] = (korisnici[korime].adresa, korisnici[korime].porta)
                return "Uspesno se priklucivte."
            else:
                return "Taa grupa ne e kreirana od organizator."
        else:
            if ime in grupi:
                grupi[ime].clenovi[korime] = (korisnici[korime].adresa, korisnici[korime].porta)
                return "Uspesno se priklucivte."
            else:
                return "Nema takva grupa"
    else:
        return "Ne ste najaveni"

def vidi_trudovi(korime):
    if korime in korisnici and korisnici[korime].najaven:
        if korisnici[korime].pozicija == 'organizator':
            return trudovi
        else:
            return "Nemate privlegii."

def isprati_korisnik(korime, korime_prati):
    if korime not in korisnici and korime_prati not in korisnici:
        return "Ne ste registrirani ili korisnikot do koj sakate da pratite ne e registriran."
    if korisnici[korime].najaven == 1 and korisnici[korime_prati].najaven == 1:
        return korisnici[korime_prati].adresa, korisnici[korime_prati].porta
    else:
        return "Ne ste najaveni ili korisnikot do koj sakate da pratite ne e najavi."

def isprati_grupa(korime,ime):
    if korime in korisnici and korisnici[korime].najaven:
        if ime in grupi and korime in grupi[ime].clenovi:
            return grupi[ime].clenovi
    else:
        return "Ne ste najaveni."

def brishi_grupa(korime, ime):
    if korime in korisnici and korisnici[korime].pozicija == 'menadzer':
        del grupi[ime]
        return "Uspeshno izbrishavte"
    else:
        return "Nemate privilegii."
    
def napusti_grupa(ime, korime):
    if ime in grupi:
        del grupi[ime].korisnici[korime]
        return "Uspesno ja napustivte grupata!"
    else:
        return "Nema takva grupa!"

def odjava(korime):
    if korime in korisnici and korisnici[korime].najaven:
        for grupa in grupi:
            if korime in grupa.clenovi:
                del grupa.clenovi[korime]
        korisnici[korime].najaven = 0
        return "Uspeshna odjava."
    else:
        return "Ne ste najaven.."

server = SimpleXMLRPCServer(('127.0.0.1',12345))
server.register_function(registracija)
server.register_function(najava)
server.register_function(prati_trud)
server.register_function(kreiraj_grupa)
server.register_function(prikluci_grupa)
server.register_function(vidi_trudovi)
server.register_function(isprati_grupa)
server.register_function(isprati_korisnik)
server.register_function(brishi_grupa)
server.register_function(napusti_grupa)
server.register_function(odjava)

print('Server up and listening..')
server.serve_forever()
