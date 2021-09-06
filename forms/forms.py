from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from __init__ import create_app
from werkzeug.utils import secure_filename
from datetime import datetime, date
from os import path
import urllib.request
import datetime 
import json
import os

# BLUEPRINTS
forms_bp = Blueprint('forms_bp', __name__,
    template_folder='templates',
    static_folder='static')

# PAGE'S REQUIREMENTS
app, mysql = create_app()

basepath = path.dirname(__file__)
app.config['UPLOAD_FOLDER'] = 'static/img'

def form_select(formreq, table):
    if formreq == 'client' and table == 'streaming_account':
        query = 'SELECT sa.id, pl.name, pl.duration FROM platform pl, streaming_account sa WHERE sa.select_platform = pl.id and sa.last_screens != 0'
    else:
        query = 'SELECT * FROM ' + table
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    data = cur.fetchall()

    return data

def get_date():
    today = date.today()
    value = today.strftime("%d/%m/%Y")
    return value

def normal(type):
    if type == 'text':
        x = 'yes'
        y = ' VARCHAR(255)'
    elif type == 'file':
        x = 'no'
        y = ' VARCHAR(255)'
    elif type == 'date':
        x = 'no'
        y = ' DATE'
    return x, y

def get_json_form(form):
    if form == 'st':
        stformFullPath = os.path.realpath('./stform.json')
        f = open(stformFullPath,)
        data = json.load(f)
    elif form == 'dy':
        dyformFullPath = os.path.realpath('./dyform.json')
        f = open(dyformFullPath,)
        data = json.load(f)
    return data, f

def platform_duration(start, end):
    year1 = int(start[0:4])
    month1 = int(start[5:7])
    day1 = int(start[8:10])
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

# PAGES
@forms_bp.route('/dynamic_form/<form>-<formreq>')
def dynamic_form(form, formreq):
    # PAYMENT_METHOD
    if formreq == 'payment_method':
        return render_template('forms/payment_method.html', user_type = session['user_type'])
    
    # GENERAL
    data, f = get_json_form(form)
    attrb = data[formreq]['attributes']
    payDict = {}
    for i in attrb:
        # Select
        if i['type'] == 'select' and i['selectTable'] != None:
            if i['selectTable'] == 'payment_method':
                dyData, d = get_json_form('dy')
                for dy in dyData:
                    dyAttrb = dyData[dy]['attributes']
                    tup = form_select('client', dy)
                    i[dy] = form_select('client', dy)
                    resp = []
                    item = {}
                    for y in tup:
                        z = 0
                        for x in dyAttrb:
                            if x['type'] == 'date':
                                date = datetime.datetime.strptime(str(y[z]), "%Y-%m-%d").strftime("%d/%m/%Y")
                                item[x['name']] = date
                            elif x['type'] == 'file':
                                file = 'file'
                                item[x['name']] = file
                            else:
                                item[x['name']] = y[z]
                            z += 1
                        resp.append(item)
                    payDict[dy] = resp
                d.close()
            i['options'] = form_select(formreq, i['selectTable'])

        # Date
        elif i['type'] == 'date':
            i['value'] = get_date()             

    f.close()
    return render_template('forms/dynamic_form.html', attrb = attrb, formreq = formreq, form = form, payDict = payDict, user_type = session['user_type'])

@forms_bp.route('/add/<form>-<formreq>', methods=['GET', 'POST'])
def add(form, formreq):
    if request.method == 'POST':
        data, f = get_json_form(form)
        attrb = data[formreq]['attributes']
        into = []
        values = []
        for i in attrb:
            if i['name'] == 'user':
                into.append(i['name']) 
                values.append('"' + session['username'] + '"')

            elif i['type'] == 'file':
                file = request.files[i['name']]
                fileName = secure_filename(file.filename)
                route = path.abspath(path.join(basepath, "static\\img\\" + fileName))
                file.save(route)
                into.append(i['name']) 
                values.append('"' + fileName + '"')

            elif i['type'] == 'checkbox':
                if i['label'] != None:
                    checkbox = request.form.getlist(i['name'])
                    string = ', '.join(checkbox)
                    into.append(i['name']) 
                    values.append('"' + string + '"')

            elif formreq == 'streaming account' and i['type'] == 'select' and i['name'] == 'select_platform':
                    checkbox = request.form.getlist(i['name'])
                    string = ', '.join(checkbox)
                    into.append(i['name']) 
                    values.append('"' + string + '"')

            elif i['type'] != 'hidden':
                if formreq == 'platform' and i['name'] == 'start_date':
                    start = request.form[i['name']]
                elif formreq == 'platform' and i['name'] == 'end_date':
                    end = request.form[i['name']]

                into.append(i['name']) 
                values.append('"' + request.form[i['name']] + '"')
            
            elif formreq == 'platform' and i['name'] == 'duration':
                duration = platform_duration(start, end)
                into.append(i['name']) 
                values.append('"' + duration + '"')
            
            elif formreq == 'streaming_account' and i['name'] == 'last_screens':
                into.append(i['name']) 
                q = 'SELECT screen_amount FROM platform WHERE id = ' + request.form['select_platform']
                cur = mysql.connection.cursor()
                cur.execute(q)
                mysql.connection.commit()
                screen_amount = cur.fetchone()[0]
                values.append('"' + str(screen_amount) + '"')

        sep = ',' 
        query = 'INSERT INTO ' + formreq + '(' + sep.join(into) + ') ' +  'VALUES (' + sep.join(values) + ')'
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        flash('Added successfully')

        if formreq == 'streaming_account':
            query2 = 'SELECT * FROM streaming_account WHERE id=(SELECT MAX(id) FROM streaming_account)'
            cur.execute(query2)
            mysql.connection.commit()
            saData = cur.fetchone()

            query3 = 'SELECT * FROM platform WHERE id = ' + str(saData[2])
            cur.execute(query3)
            mysql.connection.commit()
            plData = cur.fetchone()
            
            values1 = ['"' + str(saData[0]) + '"', '"' + plData[2] + '"', '"' + str(plData[5]) + '"', '"' + str(plData[6]) + '"', '"' + str(plData[7]) + '"','"' + plData[3] + '"', '"' + saData[5] + '"', '"' + saData[6] + '"']
            for x in range(1, plData[4] + 1):
                values1.insert(1, '"' + str(x) + '"')
                sep = ', '
                query4 = 'INSERT INTO screen (account_id, number, platform, start_date, end_date, duration, url, email, password) VALUES (' + sep.join(values1) + ')'
                cur.execute(query4)
                mysql.connection.commit()
                del values1[1]

        f.close()
    return redirect('/tables/dynamic_table/' + form + '-' + formreq)

@forms_bp.route('/add_payment_method', methods=['GET', 'POST'])
def add_payment_method():
    if request.method == 'POST':
        jsonAppend, f = get_json_form('dy')
        attributes = [{"type":"hidden", "name":"id"}, {"type":"hidden", "name":"user"}]
        
        requiredFieldsSt = []
        requiredFieldsDy = []
        i = 0
        while str(i) in request.form:
            fieldName = request.form.getlist(str(i))[0]
            fieldType = request.form.getlist(str(i))[1]
            x, y = normal(fieldType)

            jsonItem = {"type": fieldType, "label": fieldName.capitalize(), "name": fieldName, "normal":x}    
            attributes.append(jsonItem)
            requiredFieldsDy.append(fieldName + y)
            requiredFieldsSt.append(fieldName)

            i += 1

        # INSERT INTO JSON
        paymentPlatformName = request.form['payment_platform_name'].replace(" ", "_")
        jsonAppend[paymentPlatformName] = {"query":"SELECT * FROM " + paymentPlatformName + "WHERE user = ", "attributes": attributes}
        dyformFullPath = os.path.realpath('./dyform.json')
        with open(dyformFullPath, 'w') as jsonFile:
            json.dump(jsonAppend, jsonFile)
            jsonFile.close()

        # CREATE DYNAMIC TABLE
        query1 = 'CREATE TABLE ' + paymentPlatformName + ' (id INT(11) AUTO_INCREMENT PRIMARY KEY, user VARCHAR(255), ' + ', '.join(requiredFieldsDy) + ')'
        cur = mysql.connection.cursor()
        cur.execute(query1)
        mysql.connection.commit()

        # INSERT DATA INTO STATIC
        file = request.files['file_name']
        fileName = secure_filename(file.filename)
        route = path.abspath(path.join(basepath, "static\\img\\" + fileName))
        file.save(route)

        string = ', '.join(requiredFieldsSt)

        query2 = 'INSERT INTO payment_method (user, payment_platform_name, file_name, required_fields) VALUES (' + '"' + session['username'] + '", "'+ paymentPlatformName + '", "' + fileName + '", "' + string + '")'
        cur.execute(query2)
        mysql.connection.commit()
        f.close()
    return redirect('/tables/dynamic_table/st-payment_method')

@forms_bp.route('/edit/<form>-<formreq>/<id>')
def edit(form, formreq, id):
    data, f = get_json_form(form)
    attrb = data[formreq]['attributes']
    query = 'SELECT * FROM ' + formreq + ' WHERE id = ' + id
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    formData = cur.fetchall()
    payDict = {}
    for i in attrb:
        # Select
        if i['type'] == 'select' and i['selectTable'] != None:
            if i['selectTable'] == 'payment_method':
                dyData, d = get_json_form('dy')
                for dy in dyData:
                    dyAttrb = dyData[dy]['attributes']
                    tup = form_select('client', dy)
                    i[dy] = form_select('client', dy)
                    resp = []
                    item = {}
                    for y in tup:
                        z = 0
                        for x in dyAttrb:
                            if x['type'] == 'date':
                                date = datetime.datetime.strptime(str(y[z]), "%Y-%m-%d").strftime("%d/%m/%Y")
                                item[x['name']] = date
                            elif x['type'] == 'file':
                                file = 'file'
                                item[x['name']] = file
                            else:
                                item[x['name']] = y[z]
                            z += 1
                        resp.append(item)
                    payDict[dy] = resp
                d.close()
            i['options'] = form_select(formreq, i['selectTable'])

        # Date
        elif i['type'] == 'date':
            i['value'] = get_date() 
    
    f.close()
    return render_template('forms/edit.html', rowToEdit = formData[0], attrb = attrb, formreq = formreq, form = form, payDict = payDict, user_type = session['user_type'])

@forms_bp.route('/update/<form>-<formreq>/<id>', methods=['GET', 'POST'])
def update(form, formreq, id):
    if request.method == 'POST':
        data, f = get_json_form(form)
        attrb = data[formreq]['attributes']
        values = []
        for i in attrb:
            if i['name'] == 'user':
                query1 = i['name'] + ' = ' + '"' + session['username'] + '"'
                values.append(query1)

            elif i['type'] == 'file':
                file = request.files[i['name']]
                fileName = secure_filename(file.filename)
                route = path.abspath(path.join(basepath, "static\\img\\" + fileName))
                file.save(route)
                query1 = i['name'] + ' = ' + '"' + fileName + '"'
                values.append(query1)

            elif i['type'] == 'checkbox':
                if i['label'] != None:
                    checkbox = request.form.getlist(i['name'])
                    string = ', '.join(checkbox)
                    query1 = i['name'] + ' = ' + '"' + string + '"'
                    values.append(query1)

            elif formreq == 'streaming account' and i['type'] == 'select' and i['name'] == 'select_platform':
                    checkbox = request.form.getlist(i['name'])
                    string = ', '.join(checkbox)
                    values.append(i['name'] + ' = ' + '"' + string + '"')

            elif i['type'] != 'hidden':
                if formreq == 'platform' and i['name'] == 'start_date':
                    start = request.form[i['name']]
                if formreq == 'platform' and i['name'] == 'end_date':
                    end = request.form[i['name']]
                query1 = i['name'] + ' = ' + '"' + request.form[i['name']] + '"'
                values.append(query1)

            elif formreq == 'platform' and i['name'] == 'duration':
                duration = platform_duration(start, end)
                query1 = i['name'] + ' = ' + '"' + duration + '"'
                values.append(query1)
                
            elif formreq == 'streaming_account' and i['name'] == 'last_screens':
                query = 'SELECT screen_amount FROM platform WHERE id = ' + request.form['select_platform']
                cur = mysql.connection.cursor()
                cur.execute(query)
                mysql.connection.commit()
                screen_amount = cur.fetchone()[0]
                values.append(i['name'] + ' = ' + '"' + str(screen_amount) + '"')

        sep = ', '
        query2 = 'UPDATE ' + formreq + ' SET ' + sep.join(values) + ' WHERE id = ' + id
        cur = mysql.connection.cursor()
        cur.execute(query2)
        mysql.connection.commit()
        flash('Edited Successfully')
        f.close()
        return redirect('/tables/dynamic_table/' + form + '-' + formreq)

@forms_bp.route('/edit_payment_method/<name>/<id>')
def edit_payment_method(name, id):
    # DELETE FROM JSON
    query1 = 'SELECT * FROM payment_method WHERE id = ' + id
    cur = mysql.connection.cursor()
    cur.execute(query1)
    mysql.connection.commit()
    name = cur.fetchall()[0][2]
    data, f = get_json_form('dy')
    if name in data: 
        del data[name]
        open("dyform.json", "w").write(json.dumps(data)) 
        f.close()
    
    # DELETE IN STATIC TABLE
    query1 = 'DELETE FROM payment_method WHERE id = ' + id
    cur = mysql.connection.cursor()
    cur.execute(query1)
    mysql.connection.commit()

    # DELETE TABLE FROM DATABASE
    query2 = 'DROP TABLE ' + name
    cur.execute(query2)
    mysql.connection.commit()
    return render_template('forms/payment_method.html', user_type = session['user_type'])

@forms_bp.route('/delete/<form>-<formreq>/<id>')
def delete_contact(form, formreq, id):
    cur = mysql.connection.cursor()

    # DYNAMIC
    if formreq == 'payment_method':
        query1 = 'SELECT * FROM payment_method WHERE id = ' + id
        cur.execute(query1)
        mysql.connection.commit()
        name = cur.fetchall()[0][2]

        # DELETE FROM JSON
        data, f = get_json_form('dy')
        if name in data: 
            del data[name]
            open("dyform.json", "w").write(json.dumps(data)) 
            f.close()

        # DELETE TABLE FROM DATABASE
        query2 = 'DROP TABLE ' + name
        cur.execute(query2)
        mysql.connection.commit()
    
    # STATIC
    query3 = 'DELETE FROM ' + formreq + ' WHERE id = ' + id
    cur.execute(query3)
    mysql.connection.commit()
       
    flash('Deleted Succesfully')
    return redirect('/tables/dynamic_table/' + form + '-' + formreq)