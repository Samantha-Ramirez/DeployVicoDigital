from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from __init__ import create_app
import MySQLdb.cursors
from cryptography.fernet import Fernet
import json
import re
import os

# BLUEPRINT
auth_bp = Blueprint('auth_bp', __name__,
    template_folder='templates',
    static_folder='static')

# PAGE'S REQUIREMENTS
app, mysql = create_app()

stformFullPath = os.path.realpath('./stform.json')
f = open(stformFullPath,)
data = json.load(f)

def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)

# PAGES
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    token = None
    key = None
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))
        mysql.connection.commit()
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['user_type'] = account[1]
            session['username'] = account[3]
            return redirect('/')
        else:
            msg = 'Incorrect username or password!'

    return render_template('auth/login.html', msg = msg, token = token, key = key)

@auth_bp.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('user_type', None)
    session.pop('username', None)
    return redirect('/auth/login')

@auth_bp.route('/signup/<token>/<key>', methods=['GET', 'POST'])
def signup(token, key):
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'phone' in request.form and 'ci' in request.form and 'facebook' in request.form and 'instagram' in request.form:
        attrb = data['user']['attributes']
        username = request.form['username']
        email = request.form['email']
        into = []
        values = []
        for i in attrb:
            if i['name'] == 'user_type':
                into.append(i['name']) 
                if request.form['email'] == 'yobell@gmail.com':
                    values.append('"'+ 'admin' + '"')
                elif request.form['userType'] == 'Client':
                    values.append('"'+ 'client' + '"')
                elif request.form['userType'] == 'Seller':
                    values.append('"'+ 'seller' + '"')
                
            elif i['name'] == 'parent_id' and token != 'None' and key != 'None':
                into.append(i['name']) 
                token2 = token[2:-1]
                key2 = key[2:-1]
                descryptToken = decrypt(token2.encode(), key2.encode()).decode()
                values.append(descryptToken)

            elif i['type'] == 'checkbox' and i['label'] != None:
                checkbox = request.form.getlist(i['name'])
                string = ', '.join(checkbox)
                into.append(i['name']) 
                values.append('"' + string + '"')

            elif i['type'] != 'hidden':
                into.append(i['name']) 
                values.append('"' + request.form[i['name']] + '"') 
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username = %s', (username,))
        mysql.connection.commit()
        account = cur.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        else:
            sep = ',' 
            query = 'INSERT INTO user (' + sep.join(into) + ') ' +  'VALUES (' + sep.join(values) + ')'
            cur.execute(query)
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('auth/signup.html', msg = msg, token = token, key = key)

f.close()