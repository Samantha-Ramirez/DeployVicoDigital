from flask import Flask, render_template, request, redirect, url_for, flash, session
from __init__ import create_app
from cryptography.fernet import Fernet
import os


# APP
app, mysql = create_app()


# BLUEPRINTS
from auth.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from forms.forms import forms_bp
app.register_blueprint(forms_bp, url_prefix='/forms')

from tables.tables import tables_bp
app.register_blueprint(tables_bp, url_prefix='/tables')


# PAGE'S REQUIREMENTS
def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)


# PAGES
@app.route('/')
def index():
    if 'loggedin' in session:
        query = '''SELECT cl.id, cl.user, cl.name, cl.phone, pl.name, sc.number, cl.receipt 
        FROM client cl, streaming_account sa, platform pl, screen sc 
        WHERE cl.verified IS NULL AND cl.select_platform = sa.id AND sa.select_platform = pl.id AND sc.id = (SELECT MIN(id) FROM screen WHERE account_id = cl.select_platform AND client IS NULL)'''
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        reqData = cur.fetchall()

        if session['user_type'] == 'admin':
            return render_template('admin.html', username = session['username'], reqData = reqData)
        elif session['user_type'] == 'seller':
            return render_template('seller.html', username = session['username'], reqData = reqData)
        elif session['user_type'] == 'client':
            return render_template('client.html', username = session['username'])

    return redirect('/auth/login')

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE id = %s', (session['id'],))
        mysql.connection.commit()
        account = cur.fetchone()

        # REFERENCE LINK
        key = Fernet.generate_key()
        parent_id = str(session['id'])
        token = encrypt(parent_id.encode(), key)
        link = 'http://127.0.0.1:3000/referencelink'
        return render_template('profile.html', account = account, link = link, token = token, key = key, user_type = session['user_type'])
    
    return redirect('/auth/login')

@app.route('/referencelink/<token>/<key>')
def referenceLink(token, key):
    return redirect('/auth/signup/' + token + '/' + key)

@app.route('/sells_team')
def sells_team():
    if 'loggedin' in session:
        query = 'SELECT * FROM user WHERE parent_id = ' + str(session['id'])
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        data = cur.fetchall()

        return render_template('sells_team.html', username = session['username'], user_type = session['user_type'], data = data)

    return redirect('/auth/login')

@app.route('/requests/<id>', methods=['GET', 'POST'])
def requests(id):
    # Get info
    query = 'SELECT cl.select_platform, sa.last_screens FROM client cl, streaming_account sa WHERE cl.id =' + id + ' AND sa.id = cl.select_platform'
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    clData = cur.fetchone()

    # Client verified
    query2 = 'UPDATE client SET verified = "yes" WHERE id = ' + id
    cur.execute(query2)
    mysql.connection.commit()

    # Match screen and client
    query3 = 'UPDATE screen SET client = "' + id + '" WHERE account_id = ' + str(clData[0]) + ' AND id = (SELECT MIN(id) FROM screen WHERE account_id = ' + str(clData[0]) + ' AND client IS NULL)'
    cur.execute(query3)
    mysql.connection.commit()

    # Streaming account minur 1 screen
    minur = clData[1] - 1
    query4 = 'UPDATE streaming_account SET last_screens = "' + str(minur) + '" WHERE id = ' + str(clData[0])
    cur.execute(query4)
    mysql.connection.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(port = 3000, debug = True)