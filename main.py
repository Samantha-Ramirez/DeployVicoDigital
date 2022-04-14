from flask import Flask, render_template, request, redirect, url_for, flash, session
from __init__ import create_app
from cryptography.fernet import Fernet
from datetime import datetime, date
import datetime 
import os


# APP
app, mysql, environment = create_app()

# BLUEPRINTS
from auth.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from forms.forms import forms_bp
app.register_blueprint(forms_bp, url_prefix='/forms')

from tables.tables import tables_bp
app.register_blueprint(tables_bp, url_prefix='/tables')


# PAGE'S REQUIREMENTS
def platform_duration(today, end):
    year1 = int(today[0:4])
    month1 = int(today[5:7])
    day1 = int(today[8:10])
    year2 = int(end[0:4])
    month2 = int(end[5:7])
    day2 = int(end[8:10])
                                        
    d0 = date(year1, month1, day1)
    d1 = date(year2, month2, day2)
    d3 = d1 - d0
    duration = d3.days
    months = round(duration / 31)

    if months >= 1:
        duration = str(months) + ' months'
    else:
        duration = str(duration) + ' days'

    return duration 

def screenData(scData):
    today = date.today().strftime('%Y-%m-%d')
    x = 0
    for sc in scData:
        sc = list(sc)
        formatEnd = datetime.datetime.strptime(str(sc[3]), "%Y-%m-%d").strftime('%Y-%m-%d')
        sc[3] = datetime.datetime.strptime(str(sc[3]), "%Y-%m-%d").strftime('%d-%m-%Y')
        sc.insert(4, platform_duration(today, formatEnd))
        phone = sc[6]
        sc[6] = '+58' + phone[1:]
        warning = f'''Estimado cliente {sc[5]}, su cuenta de {sc[1]} bajo el email {sc[7]} se vencerá en {sc[4]}, recuerde renovar a tiempo'''
        sc.insert(8, warning)
        scData[x] = sc
        x = x + 1
    return scData

# PAGES
@app.route('/')
def index():
    if 'loggedin' in session:
        if session['user_type'] == 'admin':
            # REQUEST DATA
            query = 'SELECT rq.id, rq.date, sl.username, rq.username, rq.user_type , pl.name, sc.number, rq.receipt FROM request rq, screen sc, seller sl, platform pl WHERE sc.id = (SELECT MIN(id) FROM screen WHERE platform = rq.platform AND client IS NULL) AND sl.id = rq.seller_id AND pl.id = sc.platform AND rq.status = "not_verified" ORDER BY rq.id ASC'
            cur = mysql.connection.cursor()
            cur.execute(query)
            mysql.connection.commit()
            reqData = cur.fetchall()

            # ACTIVATED SCREENS DATA
            query1 = 'SELECT pl.file_name, pl.name, sc.duration, sc.end_date, cl.username, cl.phone, sc.email, sc.id FROM platform pl, screen sc, client cl WHERE sc.platform = pl.id AND sc.client = cl.id AND sc.client IS NOT NULL ORDER BY sc.start_date'
            cur.execute(query1)
            mysql.connection.commit()
            scData = list(cur.fetchall())
            scData = screenData(scData)
                
            return render_template('admin.html', username = session['username'], user_type = session['user_type'], reqData = reqData, scData = scData, environment = environment)
        
        elif session['user_type'] == 'seller':
            query = 'SELECT pl.file_name, pl.name, sc.duration, sc.end_date, cl.username, cl.phone, sc.email, sc.id FROM platform pl, screen sc, client cl WHERE sc.platform = pl.id AND sc.client = cl.id AND sc.client IS NOT NULL AND cl.user = ' + str(session['id']) + ' ORDER BY sc.start_date'
            cur = mysql.connection.cursor()
            cur.execute(query)
            mysql.connection.commit()
            scData = list(cur.fetchall())
            scData = screenData(scData)

            return render_template('seller.html', username = session['username'], scData = scData, environment = environment)
        
        elif session['user_type'] == 'client':
            query = 'SELECT sc.*, pl.name FROM screen sc, platform pl WHERE sc.platform = pl.id AND client = ' + str(session['id'])
            cur = mysql.connection.cursor()
            cur.execute(query)
            mysql.connection.commit()
            scData = list(cur.fetchall())
            x = 0
            for sc in scData:
                sc = list(sc)
                sc[5] = datetime.datetime.strptime(str(sc[5]), "%Y-%m-%d").strftime('%d-%m-%Y')
                scData[x] = sc
                x = x + 1
            
            return render_template('client.html', username = session['username'], scData = scData, environment = environment)

    return redirect('/auth/login')

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        if session['user_type'] == 'admin' or session['user_type'] == 'seller':
            query = 'SELECT username, phone, email, password FROM seller WHERE id = ' + str(session['id'])
        else:
            query = 'SELECT username, phone, email, password FROM client WHERE id = ' + str(session['id'])
        cur.execute(query)
        mysql.connection.commit()
        account = cur.fetchone()

        # REFERENCE LINK
        id = str(session['id'])
        if environment == 'development':
            link = 'http://127.0.0.1:3000/referencelink'
        else: 
            link = 'http://vicoweb.pythonanywhere.com/referencelink'
        return render_template('profile.html', account = account, link = link, id =  id, user_type = session['user_type'])
    
    return redirect('/auth/login')

@app.route('/referencelink/<parent_id>')
def referenceLink(parent_id):
    return redirect('/auth/signup_seller/' + parent_id)

@app.route('/sells_team')
def sells_team():
    if 'loggedin' in session:
        query = 'SELECT * FROM seller WHERE parent_id = ' + str(session['id'])
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        data = cur.fetchall()

        return render_template('sells_team.html', username = session['username'], user_type = session['user_type'], data = data)

    return redirect('/auth/login')

@app.route('/requests/<id>/<option>', methods=['GET', 'POST'])
def requests(id, option):
    if option == 'approved':
        # Get info
        query = 'SELECT rq.client_id, sa.select_platform, sa.last_screens, sa.id FROM request rq, streaming_account sa WHERE sa.select_platform = rq.platform AND rq.id =' + str(id)
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        clData = cur.fetchone()

        # Request verified
        query2 = 'UPDATE request SET status = "verified" WHERE id = ' + str(id)
        cur.execute(query2)
        mysql.connection.commit()

        # Match screen and client
        query3 = 'UPDATE screen SET client = ' + str(clData[0]) + ' WHERE id = (SELECT MIN(id) FROM screen WHERE platform = ' + str(clData[1]) + ' AND client IS NULL)'
        cur.execute(query3)
        mysql.connection.commit()

        # Streaming account minur 1 screen
        minur = clData[2] - 1
        query4 = 'UPDATE streaming_account SET last_screens = "' + str(minur) + '" WHERE id = ' + str(clData[3])
        cur.execute(query4)
        mysql.connection.commit()

        # Create format message
        query5 = 'SELECT pl.name, pl.screen_amount, sc.*, cl.username, cl.phone FROM screen sc, platform pl, client cl WHERE pl.id = sc.platform AND sc.client = cl.id AND sc.client = ' + str(clData[0])
        cur.execute(query5)
        mysql.connection.commit()
        scData = cur.fetchone()
        formatMgg = f'''
        Acceso a su perfil de {scData[0]}
        Inicio: {scData[6]}
        Fin: {scData[7]}
        🔊 Si ha usado {scData[0]} antes debe borrar los archivos temporales de su navegador y si es una aplicación debe volverla a instalar, si es Smart TV, cerrar la aplicación apague y encienda el televisor ¡No comparta su clave! Ya que {scData[0]} solo permite un máximo de {scData[1]} usuarios en la cuenta. Si comparte la cuenta tendremos que suspender y cambiar las claves de acceso.
        URL: {scData[9]}
        Email: {scData[10]}
        Clave: {scData[11]}
        Perfil: {scData[4]}
        PIN: 
        📣 TÉRMINOS Y CONDICIONES:
        1. No modifique ninguna información sobre la cuenta.
        2. No cambie el correo electrónico o la contraseña de su cuenta.
        3. No agregue ni elimine perfiles.
        4. Este es un producto digital. Entonces, después de la compra, no se puede hacer un reembolso. Solo garantía de reemplazo.'''
        user = scData[13]
        phone = scData[14]
        phone = '+58' + phone[1:]

    elif option == 'rejected':
        # Request rejected
        query1 = 'UPDATE request SET status = "rejected" WHERE id = ' + str(id)
        cur = mysql.connection.cursor()
        cur.execute(query1)
        mysql.connection.commit()
        formatMgg, user, phone = None, None, None
    info = {'formatMgg':formatMgg, 'user':user, 'phone':phone}
    return info
    
    
if __name__ == '__main__':
    app.run(port = 3000, debug = True)