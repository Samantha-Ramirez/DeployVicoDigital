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
app, mysql, environment = create_app()

if environment == 'development':
    stformFullPath = os.path.realpath('./stform.json')
else:
    stformFullPath = os.path.realpath('./deploy/stform.json')
f = open(stformFullPath,)
data = json.load(f)

# PAGES
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    parent_id = None
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        mysql.connection.commit()
        account = cur.fetchone()
        
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['user_type'] = account[1]
            session['username'] = account[3]
            return redirect('/')
        else:
            msg = 'Usuario o contraseña incorrecta!'

    return render_template('auth/login.html', msg = msg, parent_id = parent_id)

@auth_bp.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('user_type', None)
    session.pop('username', None)
    return redirect('/auth/login')

@auth_bp.route('/signup/<user_type>/<parent_id>', methods=['GET', 'POST'])
def signup_seller(parent_id, user_type):
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        attrb = data[user_type]['attributes']
        username = request.form['username']
        email = request.form['email']
        into = []
        values = []
        for i in attrb:
            if i['name'] == 'user_type':
                into.append(i['name']) 
                values.append('"'+ user_type + '"')
                
            elif i['name'] == 'parent_id' and parent_id != 'None':
                into.append(i['name']) 
                values.append(parent_id)

            elif i['type'] == 'radio' and i['label'] != None:
                radio = request.form.getlist(i['name'])
                string = ', '.join(radio)
                into.append(i['name']) 
                values.append('"' + string + '"')

            elif i['type'] != 'hidden' and i['type'] != 'radio':
                into.append(i['name']) 
                values.append('"' + request.form[i['name']] + '"') 
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE email = %s', (email,))
        mysql.connection.commit()
        account = cur.fetchone()

        if account:
            msg = 'Esta cuenta ya existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Direcci&oacute;n de correo inv&aacute;lida!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'El nombre de usuario solo debe contener car&aacute;cteres y n&uacute;meros!'
        else:
            sep = ',' 
            query = 'INSERT INTO user (' + sep.join(into) + ') ' +  'VALUES (' + sep.join(values) + ')'
            cur.execute(query)
            mysql.connection.commit()
            return redirect('/auth/login')

    elif request.method == 'POST':
        msg = 'Por favor completa el formulario!'

    if user_type == 'seller':
        return render_template('auth/signup_seller.html', msg = msg, parent_id = parent_id)
    elif user_type == 'client':
        parent_id = None
        return render_template('auth/signup_client.html', msg = msg, parent_id = parent_id)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST' and 'email' in request.form and 'newPassword' in request.form and 'confirmPassword' in request.form:
        email = request.form['email']
        newPassword = request.form['newPassword']
        confirmPassword = request.form['confirmPassword']
        if newPassword == confirmPassword:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM user WHERE email = %s', (email,))
            mysql.connection.commit()
            account = cur.fetchone()
            if account: 
                cur.execute('UPDATE user SET password = %s WHERE email = %s', (newPassword, email))
                mysql.connection.commit()
                return redirect('/auth/login')
            else:
                msg = 'Email incorrecto'
        else:
            msg = 'Las contraseñas no coinciden'
        return render_template('auth/change_password.html', msg = msg)
    else: 
        return render_template('auth/change_password.html')

f.close()