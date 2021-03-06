from bottle import *
import hashlib
import auth_public as auth

import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import os

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)

#Poročila o napakah
debug(True) #za izpise pri razvoju

#Mapa za statične vire
static_dir = "./static"

@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)

###########################################################
##################### Prva stran ##########################
###########################################################

@get('/')
def izberileto():
    username = preveriUporabnika()
    admin = ali_admin(username)
    return rtemplate('zacetna.html', username=username, admin=admin, napaka=None)

###########################################################
######################## Sezona ###########################
###########################################################

@get('/<Sezona>')#Deluje
def sezona16(Sezona):
    username = preveriUporabnika()
    admin = ali_admin(username)
    #cur = baza.cursor()
    cur.execute("SELECT IGRALEC,EKIPA,POZICIJA,STAROST,VISINA,TEZA,DRZAVA,Sezona from igralci WHERE Sezona=%s",(Sezona,))
    Sezona = cur.fetchall()
    return rtemplate('sezona.html', Sezona=Sezona, username=username, admin=admin)

@get('/<Sezona>/ekipe')#Deluje
def ekipe(Sezona):
    username = preveriUporabnika()
    admin = ali_admin(username)
    #cur = baza.cursor()
    cur.execute("""SELECT ekipe.ID,Ime_ekipe,Kratica,trenerji.TRENER, trenerji.W_sezona,trenerji.L_sezona, Sponzor_na_dresu from ekipe
                        INNER JOIN trenerji ON trenerji.EKIPA = ekipe.Kratica
                        WHERE trenerji.Sezona=%s AND ekipe.Sezona=%s
                        ORDER BY W_sezona DESC""",(Sezona,Sezona,))
    ekipe = cur.fetchall()
    return rtemplate('ekipe.html', ekipe=ekipe, username=username, admin=admin)
#Darjan: med editanjem dodana napaka= napaka, če bo potrebno pri urejanju (verjetno ne)

@get('/<Sezona>/ekipe/<EKIPA>')#Deluje
def igralciekipa(Sezona,EKIPA):
    username = preveriUporabnika()
    admin = ali_admin(username)
    #cur = baza.cursor()
    cur.execute("""SELECT IGRALEC,EKIPA,POZICIJA,STAROST,VISINA,TEZA,DRZAVA,Sezona from igralci
                                    WHERE EKIPA = %s AND Sezona =%s""",(EKIPA, Sezona,))
    igralciekipa = cur.fetchall()
    return rtemplate('igralciekipa.html', igralciekipa=igralciekipa, EKIPA=EKIPA, Sezona=Sezona, username=username, admin=admin)

@post('/<username>/priljubljeni/<IGRALEC>&<Sezona>')
def priljubljeni(username, IGRALEC, Sezona):
    username = preveriUporabnika()
    cur.execute("SELECT * FROM priljubljeni WHERE username=%s AND IGRALEC=%s", [username, IGRALEC])
    if cur.fetchone() is None:
        cur.execute("INSERT INTO priljubljeni VALUES (%s,%s)",(username, IGRALEC,))
        redirect('{0}{1}'.format(ROOT, Sezona))
    else:
        redirect('{0}{1}'.format(ROOT, Sezona))

@get('/<username>/priljubljeni')
def priljubljeni_tabela(username):
    username = preveriUporabnika()
    admin = ali_admin(username)
    cur.execute("SELECT * from priljubljeni WHERE username = %s",(username,))
    priljubljeni_tabela = cur.fetchall()
    return rtemplate('priljubljeni.html', priljubljeni_tabela=priljubljeni_tabela, username=username, admin=admin)

@get('/<username>/priljubljeni/<IGRALEC>')
def priljubljenistatistika(username,IGRALEC):
    username = preveriUporabnika()
    admin = ali_admin(username)
    #cur = baza.cursor()
    cur.execute("""SELECT IGRALEC,GP,MPG,PPG,APG,RPG,SPG,FT,DVA,TRI,Sezona from igralci WHERE IGRALEC=%s""",(IGRALEC,))
    priljubljenistatistika = cur.fetchall()
    return rtemplate('priljubljenistatistika.html', priljubljenistatistika=priljubljenistatistika, IGRALEC=IGRALEC, username=username, admin=admin)

@get('/<Sezona>/<IGRALEC>')
def igralecstatistika(Sezona,IGRALEC):
    username = preveriUporabnika()
    admin = ali_admin(username)
    #cur = baza.cursor()
    cur.execute("""SELECT IGRALEC,GP,MPG,PPG,APG,RPG,SPG,FT,DVA,TRI,Sezona from igralci WHERE IGRALEC=%s AND Sezona=%s""",(IGRALEC,Sezona,))
    igralecstatistika = cur.fetchall()
    return rtemplate('igralecstatistika.html', igralecstatistika=igralecstatistika, IGRALEC=IGRALEC, Sezona=Sezona, username=username, admin=admin)

@get('/<Sezona>/ekipe/uredi/<ID>')
def uredi_sponzorja_get(ID, Sezona):
    username = preveriUporabnika()
    admin = ali_admin(username)
    #cur = baza.cursor()
    cur.execute("SELECT ID,Ime_ekipe,Sponzor_na_dresu, Sezona FROM ekipe WHERE ID = %s", (ID,))
    ekipe = cur.fetchone()
    return rtemplate('ekipe-edit.html', ekipe=ekipe, username=username, admin=admin)


@get('/<Sezona>/ekipe/<EKIPA>/<TRENER>')#Deluje
def trenerjistatistika(TRENER,Sezona,EKIPA):
    username = preveriUporabnika()
    admin = ali_admin(username)
    #cur = baza.cursor()
    cur.execute("""SELECT TRENER,EKIPA,st_let_s_klubom,st_let_kariera,G_sezona,W_sezona,L_sezona,G_s_klubom,W_s_klubom,L_s_klubom,G_kariera,W_kariera,L_kariera,W_pr, Sezona from trenerji
                                    WHERE TRENER = %s AND Sezona=%s""",(TRENER,Sezona ))
    trenerjistatistika = cur.fetchall()
    return rtemplate('trenerjistatistika.html', trenerjistatistika=trenerjistatistika, username=username, admin=admin)


@post('/<Sezona>/ekipe/uredi/<ID>')
def uredi_sponzorja_post(ID, Sezona):
    username = preveriUporabnika()
    admin = ali_admin(username)
    Sponzor_na_dresu = request.forms.Sponzor_na_dresu
    #cur = baza.cursor()
    cur.execute("UPDATE ekipe SET Sponzor_na_dresu = %s WHERE ID = %s RETURNING sezona", (Sponzor_na_dresu, ID))
    sezona = cur.fetchone()
    redirect('{0}{1}/ekipe'.format(ROOT,str(sezona[0])))
    """ redirect('/' + str(sezona[0]) + '/ekipe') """


###########################################################
################ Registracija/Prijava #####################
###########################################################
    
# možna prijava: uporabniško ime = uporabnik, geslo = 1234 

def hashGesla(s):    #za shranjevanje gesla
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()

skrivnost = "kODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkj"  
adminGeslo = "1234"

def preveriUporabnika():
    # Dobimo username iz piškotka
    username = request.get_cookie('username', secret=skrivnost)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        cur.execute("SELECT username FROM uporabnik WHERE username=%s", [username])
        r = cur.fetchone()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return username
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    else:
        return None

def ali_admin(username):
    if username is not None:
        cur.execute("SELECT admin FROM uporabnik WHERE username=%s", [username])
        return cur.fetchone()[0]
    else:
        return False

def postani_admin():
    username = preveriUporabnika()
    adminPassword = request.forms.adminPassword
    password = request.forms.password

    if password == "":
        if adminPassword == adminGeslo:
            cur.execute("UPDATE uporabnik SET admin = True WHERE username=%s", [username])
            admin = ali_admin(username)
            return rtemplate('zacetna.html', napaka=None, username=username, admin=admin)
        else:
            admin = ali_admin(username)
            return rtemplate('zacetna.html', napaka="Vnesili ste napačno admin geslo.", username=username, admin=admin)
    else:
        cur.execute("SELECT password FROM uporabnik WHERE username=%s", [username])
        if cur.fetchone()[0] == hashGesla(password):
            cur.execute("DELETE FROM uporabnik WHERE username=%s", [username])
            response.delete_cookie('username')
            return rtemplate('zacetna.html', napaka=None, username=None, admin=None)
        else:
            admin = ali_admin(username)
            return rtemplate('zacetna.html', napaka="Vnesili ste napačno geslo.", username=username, admin=admin)

@post('/postani_admin')
def postani_admin_post():
    postani_admin()
    redirect('{0}'.format(ROOT))

@get('/registracija')
def registracija_get():
    #cur = baza.cursor()
    return rtemplate('registracija.html', username=None, napaka=None) 

@post("/registracija")
def registracija_post():
    print('trying to register')
    username = request.forms.username
    password1 = request.forms.password1
    password2 = request.forms.password2
    adminPassword = request.forms.adminPassword
    adminCheck = request.forms.adminCheckbox

    cur.execute("SELECT * FROM uporabnik WHERE username=%s", [username])
    if cur.fetchone():
        # Uporabnik že obstaja
        return rtemplate("registracija.html",
                               username=username,
                               napaka='To uporabniško ime je že zasedeno.')
    elif not password1 == password2:
        # Geslo se ne ujemata
        return rtemplate("registracija.html",
                               username=username,
                               napaka='Gesli se ne ujemata.')
    elif len(password1) < 4:
        # Prekratko geslo
        return rtemplate("registracija.html",
                               username=username,
                               napaka='Geslo mora imeti vsaj 4 znake.')
    else:
        # Vstavi novega uporabnika v bazo
        if adminCheck == "kot admin":
            if adminPassword == adminGeslo:
                password = hashGesla(password1)
                cur.execute("INSERT INTO uporabnik (username, password, admin) VALUES (%s, %s, %s)",
                            (username, password, True))
                # Daj uporabniku cookie
                response.set_cookie('username', username, secret=skrivnost)
                redirect("{0}".format(ROOT))
            else:
                return rtemplate("registracija.html",
                                username=username,
                                napaka='Admin geslo ni pravilno.')
        else:
            password = hashGesla(password1)
            cur.execute("INSERT INTO uporabnik (username, password, admin) VALUES (%s, %s, %s)",
                        (username, password, False))
            # Daj uporabniku cookie
            response.set_cookie('username', username, secret=skrivnost)
            redirect("{0}".format(ROOT)) 

@get('/prijava')
def prijava_get():
    return rtemplate('prijava.html', napaka=None)

@post('/prijava')
def prijava_post():
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo hash gesla
    password = hashGesla(request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    cur.execute("SELECT * FROM uporabnik WHERE username=%s AND password=%s", [username, password])
    if cur.fetchone() is None:
        # Username in geslo se ne ujemata
        return rtemplate("prijava.html",
                               napaka="Uporabniško ime ali geslo nista ustrezna",
                               username=username)
    else:
        # Vse OK, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, secret=skrivnost)
        redirect("{0}".format(ROOT))

@get('/odjava')
def odjava_get():
    # Pobriši cookie in preusmeri na login.
    response.delete_cookie('username')
    redirect('{0}prijava'.format(ROOT))
##########################################################################################


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

run(host='localhost', port=SERVER_PORT, reloader=RELOADER)