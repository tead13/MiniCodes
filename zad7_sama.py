from xmlrpc.server import SimpleXMLRPCServer  # Ja vnesuvame klasata za XML-RPC server, preku koja ke primame kontrolni baranja od klientite.

class korisnik():  # Klasa sto gi opisuva korisnicite vo sistemot.
    def __init__(self, pozicija, ime, korime,lozinka, najaven=0, adresa ='', porta = 0):  # Konstruktor za nov korisnik.
        self.pozicija = pozicija  # Ja cuvame pozicijata: avtor, organizator ili menadzer.
        self.ime = ime  # Go cuvame imeto na korisnikot.
        self.korime = korime  # Go cuvame korisnickoto ime.
        self.lozinka =lozinka  # Ja cuvame lozinkata.
        self.najaven = najaven  # Flag dali korisnikot e najaven ili ne.
        self.adresa = adresa  # IP adresa na klientot po najava.
        self.porta = porta  # TCP porta na klientot po najava.

class grupa():  # Klasa sto opisuvа edna grupa.
    def __init__(self, ime, admin =''):  # Konstruktor za grupa.
        self.ime = ime  # Ime na grupata.
        self.admin = admin  # Korisnicko ime na adminot/kreatorot na grupata.
        self.clenovi = {}  # Rechnik so clenovi na grupata, obicno vo forma {"korime": (adresa, porta)}.

korisnici = {}  # Glaven rechnik za site registrirani korisnici: {"korime": objekt_od_klasa_korisnik}.
grupi = {}  # Rechnik za site grupi: {"ime_grupa": objekt_od_klasa_grupa}.
trudovi = {}  # Rechnik za site trudovi: {"naslov": "link"}.

def registracija(pozicija, ime, korime, lozinka):  # Funkcija za registracija na nov korisnik.
    if korime not in korisnici:  # Proveruva dali korisnickoto ime ushte ne postoi.
        korisnici[korime] = korisnik(pozicija, ime, korime, lozinka)  # Kreira nov korisnik i go zapisuva vo rechnikot korisnici.
        return "Uspeshno se registriravte!"  # Vrakja poraka za uspesna registracija.
    else:  # Ako korisnickoto ime vekje postoi.
        return "Veke ste registrirani.."  # Vrakja poraka deka korisnikot vekje postoi.
    
def najava(korime, lozinka, adresa, porta):  # Funkcija za najava na korisnikot i zachuvuvanje na negovata IP i porta.
    if korime in korisnici:  # Proveruva dali korisnikot postoi.
        if korisnici[korime].najaven:  # Proveruva dali vekje e najaven.
            return "Veke ste najaveni!"  # Ako e najaven, vrakja poraka.
        elif korisnici[korime].lozinka == lozinka:  # Proveruva dali lozinkata e tochna.
            korisnici[korime].najaven = 1  # Go oznachuva korisnikot kako najaven.
            korisnici[korime].adresa = adresa  # Ja cuva IP adresata na klientot.
            korisnici[korime].porta = porta  # Ja cuva portata na klientot.
            return "Uspeshno se najavivte."  # Vrakja poraka za uspesna najava.
        else:  # Ako lozinkata ne e tochna.
            return "Greshna lozinka."  # Vrakja poraka za greshna lozinka.
    else:  # Ako korisnikot ne postoi vo sistemot.
        return "Ne ste registrirani so toa korisnicko ime."  # Vrakja poraka deka korisnikot ne e registriran.

def prati_trud(korime, naslov, link):  # Funkcija so koja avtorot prakja trud na serverot.
    if korime in korisnici and korisnici[korime].najaven:  # Mora korisnikot da postoi i da bide najaven.
        if korisnici[korime].pozicija == "avtor":  # Samo korisnik so pozicija avtor moze da prati trud.
            if naslov not in trudovi:  # Proveruva dali nema vekje trud so istiot naslov.
                trudovi[naslov] = link  # Go zapisuva trudot vo rechnikot trudovi.
                return "Uspesno dodaden trud."  # Vrakja poraka za uspesno dodavanje.
            else:  # Ako vekje postoi trud so istiot naslov.
                return "Veke ima takov trud."  # Vrakja poraka deka trudot vekje postoi.
        else:  # Ako korisnikot ne e avtor.
            return "Nemate privilegii na avtor."  # Nema dozvola da prati trud.
    else:  # Ako ne e najaven ili ne postoi.
        return "Ne ste najaveni."  # Vrakja poraka deka ne e najaven.

def kreiraj_grupa(korime,ime):  # Funkcija za kreiranje nova grupa.
    if korime in korisnici and korisnici[korime].najaven:  # Mora da postoi korisnikot i da e najaven.
        if korisnici[korime].pozicija == 'organizator' or korisnici[korime].pozicija == 'menadzer':  # Samo organizator ili menadzer moze da kreira grupa.
            if ime in grupi:  # Proveruva dali grupata vekje postoi.
                return "Grupata postoi."  # Ako postoi, vrakja poraka.
            else:  # Ako ne postoi.
                grupi[ime] = grupa(ime)  # Kreira nov objekt grupa i go zapisuvа vo rechnikot grupi.
                grupi[ime].admin = korime  # Go postavuva kreatorot kako admin na grupata.
                return "Uspesno kreiravte grupa"  # Vrakja poraka za uspesno kreiranje.
        else:  # Ako korisnikot nema soodvetna pozicija.
            return "Nemate privilegii"  # Nema dozvola da kreira grupa.
    else:  # Ako ne e najaven.
        return "Ne ste najaveni."  # Vrakja poraka deka ne e najaven.
    
def prikluci_grupa(korime, ime):  # Funkcija za priklucuvanje na korisnik vo grupa.
    if korime in korisnici and korisnici[korime].najaven:  # Mora da postoi i da e najaven.
        if korisnici[korime].pozicija == 'avtor':  # Ako korisnikot e avtor.
            if ime in grupi and korisnici[grupi[ime].admin].pozicija == 'organizator':  # Avtor moze da vleze samo vo grupa kreirana od organizator.
                grupi[ime].clenovi[korime] = (korisnici[korime].adresa, korisnici[korime].porta)  # Go dodava avtorot vo clenovite so negovata adresa i porta.
                return "Uspesno se priklucivte."  # Poraka za uspesno priklucuvanje.
            else:  # Ako grupata ne e od organizator ili ne postoi.
                return "Taa grupa ne e kreirana od organizator."  # Vrakja poraka za nedozvoleno priklucuvanje.
        else:  # Ako korisnikot ne e avtor, togash e drug tip korisnik.
            if ime in grupi:  # Proveruva dali grupata postoi.
                grupi[ime].clenovi[korime] = (korisnici[korime].adresa, korisnici[korime].porta)  # Go dodava korisnikot vo grupata.
                return "Uspesno se priklucivte."  # Potvrda za priklucuvanje.
            else:  # Ako nema takva grupa.
                return "Nema takva grupa"  # Vrakja poraka deka grupata ne postoi.
    else:  # Ako korisnikot ne e najaven.
        return "Ne ste najaveni"  # Vrakja poraka deka ne e najaven.

def vidi_trudovi(korime):  # Funkcija za pregled na site trudovi.
    if korime in korisnici and korisnici[korime].najaven:  # Mora da postoi korisnikot i da e najaven.
        if korisnici[korime].pozicija == 'organizator':  # Samo organizator ima privilegii da gi vidi trudovite.
            return trudovi  # Go vrakja celiot rechnik so trudovi.
        else:  # Ako korisnikot ne e organizator.
            return "Nemate privlegii."  # Vrakja poraka deka nema privilegii.

def isprati_korisnik(korime, korime_prati):  # Funkcija sto vrakja adresa i porta od korisnik do koj sakame da pratime poraka.
    if korime not in korisnici and korime_prati not in korisnici:  # Proveruva dali i isprakjachot i primachot ne se registrirani.
        return "Ne ste registrirani ili korisnikot do koj sakate da pratite ne e registriran."  # Vrakja greska.
    if korisnici[korime].najaven == 1 and korisnici[korime_prati].najaven == 1:  # Proveruva dali dvajcata se najaveni.
        return korisnici[korime_prati].adresa, korisnici[korime_prati].porta  # Ja vrakja adresata i portata na primachot.
    else:  # Ako nekoj od niv ne e najaven.
        return "Ne ste najaveni ili korisnikot do koj sakate da pratite ne e najavi."  # Vrakja greska.

def isprati_grupa(korime,ime):  # Funkcija sto gi vrakja clenovite od grupa za da se isprati poraka do site.
    if korime in korisnici and korisnici[korime].najaven:  # Mora korisnikot da e najaven.
        if ime in grupi and korime in grupi[ime].clenovi:  # Proveruva dali grupata postoi i dali korisnikot e clen vo nea.
            return grupi[ime].clenovi  # Go vrakja rechnikot so clenovi na grupata.
    else:  # Ako korisnikot ne e najaven.
        return "Ne ste najaveni."  # Vrakja poraka deka ne e najaven.

def brishi_grupa(korime, ime):  # Funkcija za brishenje grupa.
    if korime in korisnici and korisnici[korime].pozicija == 'menadzer':  # Samo menadzer moze da brishe grupa.
        del grupi[ime]  # Ja brishe grupata od rechnikot grupi.
        return "Uspeshno izbrishavte"  # Potvrda za brishenje.
    else:  # Ako nema privilegii.
        return "Nemate privilegii."  # Vrakja poraka deka nema privilegii.
    
def napusti_grupa(ime, korime):  # Funkcija za napustanje na grupa.
    if ime in grupi:  # Proveruva dali grupata postoi.
        del grupi[ime].korisnici[korime]  # OVA E GRESHKA VO KODOT: treba da bide clenovi, ne korisnici.
        return "Uspesno ja napustivte grupata!"  # Potvrda deka korisnikot izlegol od grupata.
    else:  # Ako grupata ne postoi.
        return "Nema takva grupa!"  # Vrakja poraka deka nema takva grupa.

def odjava(korime):  # Funkcija za odjava na korisnik.
    if korime in korisnici and korisnici[korime].najaven:  # Mora da postoi korisnikot i da e najaven.
        for grupa in grupi:  # OVA E LOGICHKA GRESHKA: ova vrakja klucevi od recnikot, ne objekti grupa.
            if korime in grupa.clenovi:  # OVA nema da raboti bidejki grupa tuka e string, ne objekt.
                del grupa.clenovi[korime]  # OVA isto nema da raboti od istata prichina.
        korisnici[korime].najaven = 0  # Go oznachuva korisnikot kako odjaven.
        return "Uspeshna odjava."  # Potvrda za odjava.
    else:  # Ako korisnikot ne e najaven.
        return "Ne ste najaven.."  # Vrakja poraka deka ne e najaven.

server = SimpleXMLRPCServer(('127.0.0.1',12345))  # Kreira XML-RPC server na lokalna adresa 127.0.0.1 i porta 12345.
server.register_function(registracija)  # Ja registrira funkcijata registracija kako dostupna RPC metoda.
server.register_function(najava)  # Ja registrira funkcijata najava.
server.register_function(prati_trud)  # Ja registrira funkcijata prati_trud.
server.register_function(kreiraj_grupa)  # Ja registrira funkcijata kreiraj_grupa.
server.register_function(prikluci_grupa)  # Ja registrira funkcijata prikluci_grupa.
server.register_function(vidi_trudovi)  # Ja registrira funkcijata vidi_trudovi.
server.register_function(isprati_grupa)  # Ja registrira funkcijata isprati_grupa.
server.register_function(isprati_korisnik)  # Ja registrira funkcijata isprati_korisnik.
server.register_function(brishi_grupa)  # Ja registrira funkcijata brishi_grupa.
server.register_function(napusti_grupa)  # Ja registrira funkcijata napusti_grupa.
server.register_function(odjava)  # Ja registrira funkcijata odjava.

print('Server up and listening..')  # Pecati poraka deka serverot e startuvan.
server.serve_forever()  # Serverot vleguva vo beskonecna petlja i postojano prima RPC baranja.