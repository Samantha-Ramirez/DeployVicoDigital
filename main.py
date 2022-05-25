from flask import Flask, render_template, request, redirect, url_for, flash, session
from __init__ import create_app
from cryptography.fernet import Fernet
from datetime import datetime, date, timedelta
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
def duration_days(start, end):
    year1 = int(start[0:2])
    month1 = int(start[3:5])
    day1 = int(start[6:10])
    year2 = int(end[0:2])
    month2 = int(end[3:5])
    day2 = int(end[6:10])
                                        
    d0 = date(day1, month1, year1)
    d1 = date(day2, month2, year2)
    d3 = d1 - d0
    duration = d3.days
    return duration

def duration_months(start, end):
    duration = duration_days(start, end) 
    months = round(duration / 31)

    if months >= 1:
        duration = str(months) + ' meses'
    else:
        duration = str(duration) + ' días'
    return duration

def screenDataFormat(scData, user_type):
    today = date.today().strftime('%d-%m-%Y')
    x = 0
    for sc in scData:
        sc = list(sc)
        if user_type == 'admin':
            sc[3] = datetime.datetime.strptime(str(sc[3]), "%Y-%m-%d").strftime("%d-%m-%Y")
            sc[4] = datetime.datetime.strptime(str(sc[4]), "%Y-%m-%d").strftime("%d-%m-%Y")
            # ADD DURATION
            sc.append(duration_months(sc[3], sc[4]))
            # ADD DAYS LEFT 
            sc.append(duration_months(today, sc[4]))
            phone = sc[7]
            sc[7] = '+58' + phone[1:]
            warning = f'''Estimado cliente {sc[6]}, su cuenta de {sc[1]} bajo el email {sc[2]} se vencerá el {sc[4]}, recuerde renovar a tiempo'''
            sc.append(warning)
        elif user_type == 'user':
            sc[3] = datetime.datetime.strptime(str(sc[3]), "%Y-%m-%d").strftime("%d-%m-%Y")
            sc[4] = datetime.datetime.strptime(str(sc[4]), "%Y-%m-%d").strftime("%d-%m-%Y")
            sc.append(duration_months(today, sc[4]))
            daysLeft = duration_days(today, sc[4])
            if daysLeft <= 5:
                badgeColor = 'danger'
            elif daysLeft <= 10:
                badgeColor = 'warning'
            else:
                badgeColor = 'success'
            sc.append(badgeColor)
        scData[x] = sc
        x = x + 1
    return scData

# PAGES
@app.route('/')
def index():
    # CATALOGE  
    cur = mysql.connection.cursor()
    cur.execute('SELECT sa.id, pl.name, sa.start_date, sa.end_date, sa.price, pl.file_name FROM streaming_account sa, platform pl WHERE sa.select_platform = pl.id AND sa.last_screens != 0')
    mysql.connection.commit()
    dispSa = list(cur.fetchall())

    # DATE FORMAT AND ADD DURATION 
    x = 0
    for sa in dispSa:
        sa = list(sa)
        sa[2] = datetime.datetime.strptime(str(sa[2]), "%Y-%m-%d").strftime('%d-%m-%Y')
        sa[3] = datetime.datetime.strptime(str(sa[3]), "%Y-%m-%d").strftime('%d-%m-%Y')
        sa.append(duration_months(sa[2], sa[3]))
        dispSa[x] = sa
        x = x + 1

    # DIFFERENT VIEWS
    if 'loggedin' in session:
        if session['user_type'] == 'admin':
            # REQUEST DATA
            query = 'SELECT rq.id, us.username, pm.payment_platform_name, pm.data, rq.amount, rq.reference FROM recharge_request rq, user us, payment_method pm WHERE us.id = rq.user AND rq.payment_method = pm.id AND rq.status = "no verificado" ORDER BY rq.id ASC'
            cur = mysql.connection.cursor()
            cur.execute(query)
            mysql.connection.commit()
            reqData = cur.fetchall()

            # ACTIVATED SCREENS DATA
            query1 = 'SELECT sc.id, pl.name, sa.email, sc.start_date, sc.end_date, pl.file_name, us.username, us.phone, us.email FROM platform pl, screen sc, user us, streaming_account sa WHERE sc.platform = pl.id AND sc.client = us.id AND sc.account_id = sa.id AND sc.client IS NOT NULL ORDER BY sc.start_date'
            cur.execute(query1)
            mysql.connection.commit()
            actSc = list(cur.fetchall())
            actSc = screenDataFormat(actSc, 'admin')
                
            return render_template('admin.html', username = session['username'], user_type = session['user_type'], reqData = reqData, actSc = actSc, environment = environment)
        
        elif session['user_type'] == 'seller' or session['user_type'] == 'client':
            # ACTIVATED SCREENS DATA
            query1 = 'SELECT sc.id, pl.name, pl.url, sc.start_date, sc.end_date, sa.email, sa.password, sc.month_pay, pl.file_name, sa.price FROM platform pl, screen sc, streaming_account sa WHERE sc.platform = pl.id AND sc.account_id = sa.id AND sc.client = ' + str(session['id']) + ' ORDER BY sc.start_date'
            cur.execute(query1)
            mysql.connection.commit()
            actSc = list(cur.fetchall())
            actSc = screenDataFormat(actSc, 'user')

            return render_template('user.html', username = session['username'], dispSa = dispSa, actSc = actSc, environment = environment)
    return render_template('everybody.html', dispSa = dispSa, environment = environment)

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        # DATOS PERSONALES 
        cur = mysql.connection.cursor()
        query = 'SELECT username, phone, email, password FROM user WHERE id = ' + str(session['id'])
        cur.execute(query)
        mysql.connection.commit()
        account = cur.fetchone()

        query1 = 'SELECT wl.amount, rr.date FROM wallet wl, recharge_request rr WHERE rr.user = ' + str(session['id']) + ' AND wl.user = ' + str(session['id']) + ' AND rr.date IN (SELECT max(date) FROM recharge_request)'
        cur.execute(query1)
        mysql.connection.commit()
        money = cur.fetchone()
        if money:
            money = money
        else:
            money = ['Sin saldo', 'Usted no ha recargado']

        # SELLS TEAM
        query = 'SELECT * FROM user WHERE parent_id = ' + str(session['id'])
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        dataTeam = cur.fetchall() 

        # REFERENCE LINK
        id = str(session['id'])
        if environment == 'development':
            link = 'http://127.0.0.1:3000/referencelink'
        else: 
            link = 'https://vicoweb.pythonanywhere.com/referencelink'

        return render_template('profile.html', account = account, money = money, link = link, id =  id, user_type = session['user_type'], dataTeam = dataTeam)
    
    return redirect('/auth/login')

@app.route('/referencelink/<parent_id>')
def referenceLink(parent_id):
    return redirect('/auth/signup/seller/' + parent_id)

@app.route('/delete_notification/<id>', methods=['GET', 'POST'])
def delete_notification(id):
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        query = 'DELETE FROM notifications WHERE id = ' + str(id)
        cur.execute(query)
        mysql.connection.commit()
    return redirect('/auth/login')

@app.route('/fetch_notification', methods=['GET', 'POST'])
def fetch_notification():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        query1 = 'SELECT * FROM notifications nt, user us WHERE nt.user = us.id AND us.id = ' + str(session['id'])
        cur.execute(query1)
        mysql.connection.commit()
        notifications = list(cur.fetchall())
        i = 0
        for n in notifications:
            n = list(n)
            n[2] = datetime.datetime.strptime(str(n[2]), "%Y-%m-%d").strftime('%d-%m-%Y')
            notifications[i] = n
            i = i + 1
        notifications = {'notifications': notifications}
        return notifications
    return redirect('/auth/login')

@app.route('/buy_account/<saId>', methods=['GET', 'POST'])
def buy_account(saId):
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        # ACCOUNT DATA
        query = 'SELECT * FROM streaming_account WHERE id = ' + str(saId)
        cur.execute(query)
        mysql.connection.commit()
        saData = cur.fetchone()

        # WALLET
        clId = str(session['id'])
        query1 = 'SELECT amount FROM wallet WHERE user = ' + clId
        cur.execute(query1)
        mysql.connection.commit()
        usAmount = cur.fetchone()

        # COMPARATION
        if usAmount != None and saData[9] <= usAmount[0]:
            newAmount = usAmount[0] - saData[9]
            # SUBTRACTION
            query2 = 'UPDATE wallet SET amount = ' + str(newAmount) + ' WHERE user = ' + clId
            cur.execute(query2)
            mysql.connection.commit()

            # ASIGN SCREEN
            query3 = 'UPDATE screen SET client = ' + clId + ' WHERE id = (SELECT * FROM (SELECT MIN(id) FROM screen WHERE account_id = ' + str(saId) + ' AND client IS NULL) a)'
            cur.execute(query3)
            mysql.connection.commit()

            # LAST SCREENS - 1
            minur = saData[8] - 1
            query4 = 'UPDATE streaming_account SET last_screens = "' + str(minur) + '" WHERE id = ' + str(saId)
            cur.execute(query4)
            mysql.connection.commit()

            # GIVE DATA OF SCREEN
            query5 = 'SELECT pl.name, sc.start_date, sc.end_date, pl.url, sa.email, sa.password, sc.profile, us.username FROM screen sc, platform pl, user us, streaming_account sa WHERE pl.id = sc.platform AND sa.id = sc.account_id AND sc.client = us.id AND sc.account_id = ' + str(saId) + ' AND sc.client = ' + clId
            cur.execute(query5)
            mysql.connection.commit()
            scData = cur.fetchone()
            accepted = True 
            screenData = f'''
            <b>Acceso a su perfil de {scData[0]}</b><br>
            <b>Inicio: </b>{scData[1]}<br>
            <b>Fin: </b>{scData[2]}<br>
            🔊 Si ha usado {scData[0]} antes debe borrar los archivos temporales de su navegador y si es una aplicación debe volverla a instalar, si es Smart TV, cerrar la aplicación apague y encienda el televisor ¡No comparta su clave! Ya que {scData[0]} solo permite un máximo de usuarios en la cuenta. Si comparte la cuenta tendremos que suspender y cambiar las claves de acceso.<br>
            <b>URL: </b><a href="{scData[3]}" target="_blank">{scData[3]}<a><br>
            <b>Email: </b>{scData[4]}<br>
            <b>Clave: </b>{scData[5]}<br>
            <b>Perfil: </b>{scData[6]}<br>
            <b>📣 TÉRMINOS Y CONDICIONES</b><br>
            1. No modifique ninguna información sobre la cuenta.<br>
            2. No cambie el correo electrónico o la contraseña de su cuenta.<br>
            3. No agregue ni elimine perfiles.<br>
            4. Este es un producto digital. Entonces, después de la compra, no se puede hacer un reembolso. Solo garantía de reemplazo.'''
        else:
            accepted = False
            screenData = None
    else:
        accepted = 'login'
        screenData = None
    feedback = {'accepted': accepted, 'screenData': screenData}
    return feedback

@app.route('/renew_account/<scId>', methods=['GET', 'POST'])
def renew_account(scId):
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        # ACCOUNT DATA
        query = 'SELECT sc.*, sa.price FROM screen sc, streaming_account sa WHERE sc.account_id = sa.id AND sc.id = ' + str(scId)
        cur.execute(query)
        mysql.connection.commit()
        scData = cur.fetchone()

        # WALLET
        clId = str(session['id'])
        query1 = 'SELECT amount FROM wallet WHERE user = ' + clId
        cur.execute(query1)
        mysql.connection.commit()
        usAmount = cur.fetchone()

        # COMPARATION
        if usAmount != None and scData[8] <= usAmount[0]:
            newAmount = usAmount[0] - scData[8]
            # SUBTRACTION
            query2 = 'UPDATE wallet SET amount = ' + str(newAmount) + ' WHERE user = ' + clId
            cur.execute(query2)
            mysql.connection.commit()

            # CHANGING START-DATE AND END-DATE 
            startDate = scData[4]
            endDate = scData[5]
            startDateFormat = datetime.datetime.strptime(str(startDate), "%Y-%m-%d").strftime("%d-%m-%Y")
            endDateFormat = datetime.datetime.strptime(str(endDate), "%Y-%m-%d").strftime("%d-%m-%Y")
            duration = duration_days(startDateFormat, endDateFormat)
            newEndDate = endDate + timedelta(days=duration)
            query3 = 'UPDATE screen SET start_date = "' + str(endDate) + '", end_date = "' + str(newEndDate) + '" WHERE id = ' + scId
            cur.execute(query3)
            mysql.connection.commit()            

            accepted = True 
        else:
            accepted = False
    feedback = {'accepted': accepted}
    return feedback

@app.route('/recharge_request/<id>/<option>', methods=['GET', 'POST'])
def recharge_request(id, option):
    # Get info
    query = 'SELECT rq.user, rq.amount, rq.reference FROM recharge_request rq, user us WHERE rq.user = us.id AND rq.id =' + str(id)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    rqData = cur.fetchone()
    if option == 'approved':
        # Request verified
        query2 = 'UPDATE recharge_request SET status = "verificado" WHERE id = ' + str(id)
        cur.execute(query2)
        mysql.connection.commit()

        # Add money in wallet
        query3 = 'SELECT * FROM wallet WHERE user = ' + str(rqData[0])
        cur.execute(query3)
        mysql.connection.commit()
        account = cur.fetchone()
        if account:
            amount = account[2] + rqData[1]
            query4 = 'UPDATE wallet SET amount = ' + str(amount) + ' WHERE user = ' + str(rqData[0])
            cur.execute(query4)
            mysql.connection.commit()
        else:
            amount = rqData[1]
            query4 = 'INSERT INTO wallet (user, amount) VALUES (' + str(rqData[0]) + ', ' + str(amount) + ')'
            cur.execute(query4)
            mysql.connection.commit()
        feedback = 'Tu solicitud por Bs. ' + str(rqData[1]) + ' fue aceptada'

    elif option == 'rejected':
        # Request rejected
        query = 'DELETE FROM recharge_request WHERE id = ' + str(id)

        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        feedback = 'Tu solicitud por Bs. ' + str(rqData[1]) + ' fue rechazada'
    
    today = date.today().strftime('%Y-%m-%d')
    query5 = 'INSERT INTO notifications (user, date, content) VALUES (' + str(rqData[0]) + ', "' + today + '", "' +  feedback + '")'
    cur.execute(query5)
    mysql.connection.commit()
    return feedback 
    
if __name__ == '__main__':
    app.run(port = 3000, debug = True)