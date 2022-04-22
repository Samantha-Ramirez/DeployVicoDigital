from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from __init__ import create_app
import datetime 
import json
import os

# BLUEPRINTS
tables_bp = Blueprint('tables_bp', __name__,
    template_folder='templates')

# PAGE'S REQUIREMENTS
app, mysql, environment = create_app()

def get_json_form(form):
    if form == 'st':
        if environment == 'development':
            stformFullPath = os.path.realpath('./stform.json')
        else:
            stformFullPath = os.path.realpath('./deploy/stform.json')
        f = open(stformFullPath,)
        data = json.load(f)
    elif form == 'dy':
        if environment == 'development':
            dyformFullPath = os.path.realpath('./dyform.json')
        else:
            dyformFullPath = os.path.realpath('./deploy/dyform.json')
        f = open(dyformFullPath,)
        data = json.load(f)
    return data, f

# PAGES
@tables_bp.route('/dynamic_table/<form>-<formreq>')
def dynamic_table(form, formreq):
    if 'loggedin' in session:
        data, f = get_json_form(form)
        attrb = data[formreq]['attributes']
        label = data[formreq]['label']
        query = data[formreq]['query']

        if form == 'dy':
            query = query + str(session['id'])
            
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        tableData = list(cur.fetchall())

        # Finding the index
        index = 0
        fileIndex = None
        for i in attrb:
            if i['type'] == 'file':
                fileIndex = index
            elif i['type'] == 'date':
                x = 0
                for tb in tableData:
                    tb = list(tb)
                    tb[index] = datetime.datetime.strptime(str(tb[index]), "%Y-%m-%d").strftime('%d-%m-%Y')
                    tableData[x] = tb
                    x = x + 1
            index = index + 1

        return render_template('tables/dynamic_table.html', formreq = formreq, attrb = attrb, tableData = tableData, fileIndex = fileIndex, form = form, user_type = session['user_type'], environment = environment, label = label)
        f.close()
        
    return redirect('/auth/login')