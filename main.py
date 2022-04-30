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
            query = 'SELECT rq.id, us.username, pm.payment_platform_name, pm.data, rq.amount, rq.reference FROM recharge_request rq, user us, payment_method pm WHERE us.id = rq.user AND rq.payment_method = pm.id AND rq.status = "no verificado" ORDER BY rq.id ASC'
            cur = mysql.connection.cursor()
            cur.execute(query)
            mysql.connection.commit()
            reqData = cur.fetchall()

            # ACTIVATED SCREENS DATA
            query1 = 'SELECT pl.file_name, pl.name, sc.duration, sc.end_date, us.username, us.phone, sc.email, sc.id FROM platform pl, screen sc, user us WHERE sc.platform = pl.id AND sc.client = us.id AND sc.client IS NOT NULL ORDER BY sc.start_date'
            cur.execute(query1)
            mysql.connection.commit()
            scData = list(cur.fetchall())
            scData = screenData(scData)
                
            return render_template('admin.html', username = session['username'], user_type = session['user_type'], reqData = reqData, scData = scData, environment = environment)
        
        elif session['user_type'] == 'seller' or session['user_type'] == 'client':
            # CATALOGE  
            cur = mysql.connection.cursor()
            cur.execute('SELECT pl.name, sa.start_date, sa.end_date, sa.duration, pl.file_name, sa.id FROM streaming_account sa, platform pl WHERE sa.select_platform = pl.id')
            mysql.connection.commit()
            scData = list(cur.fetchall())
            # DATE FORMAT
            x = 0
            for sc in scData:
                sc = list(sc)
                sc[1] = datetime.datetime.strptime(str(sc[1]), "%Y-%m-%d").strftime('%d-%m-%Y')
                sc[2] = datetime.datetime.strptime(str(sc[2]), "%Y-%m-%d").strftime('%d-%m-%Y')
                scData[x] = sc
                x = x + 1

            # ACTIVATED SCREENS  
            return render_template('user.html', username = session['username'], scData = scData, environment = environment)
    return redirect('/auth/login')

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        # DATOS PERSONALES 
        cur = mysql.connection.cursor()
        query = 'SELECT username, phone, email, password FROM user WHERE id = ' + str(session['id'])
        cur.execute(query)
        mysql.connection.commit()
        account = cur.fetchone()

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
            link = 'http://vicoweb.pythonanywhere.com/referencelink'

        return render_template('profile.html', account = account, link = link, id =  id, user_type = session['user_type'], dataTeam = dataTeam)
    
    return redirect('/auth/login')

@app.route('/referencelink/<parent_id>')
def referenceLink(parent_id):
    return redirect('/auth/signup_seller/' + parent_id)

@app.route('/recharge_request/<id>/<option>', methods=['GET', 'POST'])
def requests(id, option):
    if option == 'approved':
        # Get info
        query = 'SELECT rq.user, rq.amount, rq.reference FROM recharge_request rq, user us WHERE rq.user = us.id AND rq.id =' + str(id)
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        rqData = cur.fetchone()

        # Request verified
        query2 = 'UPDATE recharge_request SET status = "verificado" WHERE id = ' + str(id)
        cur.execute(query2)
        mysql.connection.commit()

        # Add money in wallet
        query2 = 'SELECT * FROM wallet WHERE id = ' + str(rqData[0])
        cur.execute(query2)
        mysql.connection.commit()
        account = cur.fetchone()
        if account:
            amount = account[2] + rqData[1]
            query2 = 'UPDATE wallet SET amount = ' + str(amount) + 'WHERE id = ' + str(id)
            cur.execute(query2)
            mysql.connection.commit()
        else:
            amount = rqData[1]
            query2 = 'INSERT INTO wallet (user, amount) VALUES (' + str(rqData[0]) + ', ' + str(amount) + ')'
            cur.execute(query2)
            mysql.connection.commit()
        feedback = 'Tu solicitud con la referencia ' + str(rqData[2]) + ' por Bs. ' + str(rqData[1]) + ' fue aceptada'

    elif option == 'rejected':
        # Request rejected
        query3 = 'UPDATE recharge_request SET status = "rechazado" WHERE id = ' + str(id)
        cur = mysql.connection.cursor()
        cur.execute(query3)
        mysql.connection.commit()
        feedback = 'Tu solicitud con la referencia ' + str(rqData[2]) + ' por Bs. ' + str(rqData[1]) + ' fue rechazada'
    
    query4 = 'INSERT INTO notifications (user, content) VALUES (' + str(rqData[0]) + ', "' +  feedback + '")'
    cur.execute(query4)
    mysql.connection.commit()
    return feedback 
    
if __name__ == '__main__':
    app.run(port = 3000, debug = True)