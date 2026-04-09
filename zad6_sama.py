from xmlrpc.server import SimpleXMLRPCServer  # Ja vnesuvame klasata za XML-RPC server, so koja serverot ke prima kontrolni baranja od klientite.

class korisnik():  # Klasa za eden korisnik vo sistemot.
    def __init__(self,korime,lozinka, najaven=0, adresa ='', porta = 0):  # Konstruktor za korisnikot.
        self.korime = korime  # Go cuvame korisnickoto ime.
        self.lozinka =lozinka  # Ja cuvame lozinkata.
        self.najaven = najaven  # Flag dali korisnikot e najaven ili ne.
        self.adresa = adresa  # Ja cuvame IP adresata na klientot po najava.
        self.porta = porta  # Ja cuvame portata na klientot po najava.

class grupa():  # Klasa za grupa.
    def __init__(self, ime):  # Konstruktor za grupa.
        self.ime = ime  # Go cuvame imeto na grupata.
        self.clenovi = {}  # Rechnik so clenovi na grupata vo forma {"korime": (adresa, porta)}.

korisnici = {}  # Glaven rechnik za site registrirani korisnici: {"korime": objekt_od_klasa_korisnik}.
grupi = {} # {"Grupa1": (ime:grupa1, clenovi:{ime:clen1,....})}  # Rechnik za site grupi, kade kluch e imeto na grupata, a vrednost e objekt grupa.

def registracija(korime, lozinka):  # Funkcija za registracija na nov korisnik.
    if korime in korisnici:  # Proveruva dali korisnickoto ime vekje postoi vo rechnikot korisnici.
        return "Korisnickoto ime e zafateno."  # Ako postoi, vrakja poraka deka imeto e zafateno.
    else:  # Ako ne postoi takvo korisnicko ime.
        korisnici[korime] = korisnik(korime, lozinka)  # Kreira nov objekt korisnik i go dodava vo rechnikot korisnici.
        return "Uspeshna registracija."  # Vrakja poraka za uspesna registracija.

def najava(korime, lozinka, ipaddr, port):  # Funkcija za najava na korisnikot i zachuvuvanje na negovata adresa i porta.
    if korime in korisnici and korisnici[korime].lozinka == lozinka:  # Proveruva dali korisnikot postoi i dali lozinkata mu e tochna.
        korisnici[korime].adresa = ipaddr  # Ja zapisuva IP adresata na klientot vo objektot korisnik.
        korisnici[korime].porta = port  # Ja zapisuva portata na klientot vo objektot korisnik.
        korisnici[korime].najaven = 1  # Go oznachuva korisnikot kako najaven.

        return "Uspeshna najava."  # Vrakja poraka deka najavata e uspesna.
    else:  # Ako korisnickoto ime ne postoi ili lozinkata ne e tochna.
        return "Greshna lozinka ili korisnicko ime."  # Vrakja poraka za neuspesna najava.


def odjava(korime):  # Funkcija za odjava na korisnikot.
    if korime in korisnici and korisnici[korime].najaven == 1:  # Proveruva dali korisnikot postoi i dali e najaven.
        korisnici[korime].najaven = 0  # Go oznachuva korisnikot kako odjaven.
        for grupa in grupi:  # OVA E LOGICHKA GRESHKA: tuka grupa ke bide kluch od recnikot, ne objekt grupa.
            if korime not in grupa.clenovi:  # OVA nema da raboti bidejki grupa e string, a ne objekt so clenovi.
                del grupa.clenovi[korime]  # OVA isto nema da raboti od istata prichina.
        return "Uspeshno se odjavivte."  # Vrakja poraka za uspesna odjava.
    else:  # Ako korisnikot ne postoi ili ne e najaven.
        return "Greshka pri odjavuvanje."  # Vrakja poraka za neuspesna odjava.

def kreiraj_grupa(ime):  # Funkcija za kreiranje nova grupa.
    if ime in grupi:  # Proveruva dali vekje postoi grupa so toa ime.
        return "Veke postoi grupa so takvo ime."  # Ako postoi, vrakja poraka deka grupata vekje postoi.
    else:  # Ako ne postoi grupa so toa ime.
        grupi[ime] = grupa(ime)  # Kreira nov objekt grupa i go stava vo rechnikot grupi.
        return "Uspeshno kreirana grupa!"  # Vrakja poraka za uspesno kreiranje.

def prikluci_grupa(ime,korime):  # Funkcija za priklucuvanje na korisnik vo grupa.
    if korime in korisnici and korisnici[korime].najaven == 1:  # Proveruva dali korisnikot postoi i dali e najaven.
        if ime in grupi and korime not in grupi[ime].clenovi:  # Proveruva dali grupata postoi i dali korisnikot se ushте ne e clen.
            grupi[ime].clenovi[korime] = (korisnici[korime].adresa, korisnici[korime].porta)  # Go dodava korisnikot vo clenovite na grupata so negovata adresa i porta.

            return "Uspehsno se priklucivte na grupata."  # Vrakja poraka deka korisnikot uspesno se prikluchil.
        else:  # Ako grupata ne postoi ili korisnikot vekje e clen.
            return "Ne postoi takva grupa./Veke ste clen na grupata."  # Vrakja poraka za greshka.
    else:  # Ako korisnikot ne e najaven.
        return "Ne ste najaveni."  # Vrakja poraka deka korisnikot ne e najaven.

def prati_korisnik(korime, korime_prati):  # Funkcija shto vrakja adresa i porta na korisnik do koj sakame da pratime poraka.
    if korime not in korisnici and korime_prati not in korisnici:  # Proveruva dali i isprakjachot i primachot ne postojat vo sistemot.
        return "Ne ste registrirani ili korisnikot do koj sakate da pratite ne e registriran."  # Vrakja poraka za greshka.
    if korisnici[korime].najaven == 1 and korisnici[korime_prati].najaven == 1:  # Proveruva dali i dvajcata korisnici se najaveni.
        return korisnici[korime_prati].adresa, korisnici[korime_prati].porta  # Ja vrakja adresata i portata na primachot.
    else:  # Ako nekoj od niv ne e najaven.
        return "Ne ste najaveni ili korisnikot do koj sakate da pratite ne e najavi."  # Vrakja poraka deka nekoj ne e najaven.

def isprati_grupa(korime, ime):  # Funkcija shto gi vrakja clenovite od grupata za grupno prakjanje poraki.
    if korime not in korisnici:  # Proveruva dali isprakjachot voopsto postoi vo sistemot.
        return "Ne ste registrirani."  # Ako ne postoi, vrakja poraka deka ne e registriran.
    if korisnici[korime].najaven:  # Proveruva dali korisnikot e najaven.
        print(type(grupi[ime].clenovi))  # Go pechati tipot na clenovi, verojatno za proverka/dabagiranje.
        print(grupi[ime].clenovi)  # Go pechati samiot rechnik na clenovi, isto za dabagiranje.
        return grupi[ime].clenovi  # Go vrakja rechnikot so clenovi na grupata.
    
#?dali ovdeka gi povikuva funkc  # Tvoj komentar: ovde ne gi povikuva direktno, tuku gi registrira za da moze klientot da gi povikuva preku RPC.
server = SimpleXMLRPCServer(('127.0.0.1',12345))  # Kreira XML-RPC server shto slusha na lokalna adresa 127.0.0.1 i porta 12345.
server.register_function(najava)  # Ja registrira funkcijata najava kako RPC metoda.
server.register_function(registracija)  # Ja registrira funkcijata registracija kako RPC metoda.
server.register_function(prati_korisnik)  # Ja registrira funkcijata prati_korisnik kako RPC metoda.
server.register_function(isprati_grupa)  # Ja registrira funkcijata isprati_grupa kako RPC metoda.
server.register_function(odjava)  # Ja registrira funkcijata odjava kako RPC metoda.
server.register_function(kreiraj_grupa)  # Ja registrira funkcijata kreiraj_grupa kako RPC metoda.
server.register_function(prikluci_grupa)  # Ja registrira funkcijata prikluci_grupa kako RPC metoda.

print("Server up and listening..")  # Pechati poraka deka serverot e startuvan.
server.serve_forever()  # Serverot vleguva vo beskonecna petlja i postojano cheka RPC baranja.