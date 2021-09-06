from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from __init__ import create_app
import datetime 
import json
import os

# BLUEPRINTS
tables_bp = Blueprint('tables_bp', __name__,
    template_folder='templates')

# PAGE'S REQUIREMENTS
app, mysql = create_app()

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

def dateFormat(tableData, index):
    date = None
    for d in tableData:
        for i in d:
            if i == d[index] and index != 0:
                date = datetime.datetime.strptime(str(i), "%Y-%m-%d").strftime("%d/%m/%Y")
    return date

# PAGES
@tables_bp.route('/dynamic_table/<form>-<formreq>')
def dynamic_table(form, formreq):
    if 'loggedin' in session:
        data, f = get_json_form(form)
        attrb = data[formreq]['attributes']
        query = data[formreq]['query']
        if form == 'dy' or (formreq == 'client' and session['user_type'] != 'admin'):
            query = query + '"' + session['username'] + '"'

        elif formreq == 'client' and session['user_type'] == 'admin':
            query = "SELECT cl.id, cl.user, cl.name, cl.phone, cl.email, pl.name, pm.payment_platform_name, cl.receipt FROM client cl, streaming_account sa, platform pl, payment_method pm WHERE cl.select_platform = sa.id AND sa.select_platform = pl.id AND pm.id = cl.select_payment_method"
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        tableData = cur.fetchall()

        # Finding the index
        index = 0
        fileIndex = None
        dateIndex = 0
        dateIndex2 = 0
        x = 1
        for i in attrb:
            if i['type'] == 'file':
                fileIndex = index
            elif i['type'] == 'date':
                if x == 1:
                    dateIndex = index
                elif x == 2:
                    dateIndex2 = index
                x = x + 1
            index = index + 1
        
        # Changing the date format
        date = dateFormat(tableData, dateIndex)
        date2 = dateFormat(tableData, dateIndex2)

        return render_template('tables/dynamic_table.html', formreq = formreq, attrb = attrb, tableData = tableData, 
        fileIndex = fileIndex, dateIndex = dateIndex, date = date, dateIndex2 = dateIndex2, date2 = date2, 
        form = form, user_type = session['user_type'])
        
        f.close()
    return redirect('/auth/login')