import os
import sqlite3
from flask import Flask, jsonify, json, render_template,request, send_file
import pandas as pd
from werkzeug.utils import secure_filename
from markupsafe import escape
from werkzeug.security import safe_join
import numpy as np
import glob
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO

import BiGrams
from pandas import DataFrame
import datetime


app = Flask(__name__)

app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emidsdb.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
emidsdb = SQLAlchemy(app)

class hospital(emidsdb.Model):
    hospital_id = emidsdb.Column(emidsdb.Integer, primary_key=True)
    username = emidsdb.Column(emidsdb.String(20), nullable=False,unique=True)
    password = emidsdb.Column(emidsdb.String(80), nullable=False)
    hospital_name = emidsdb.Column(emidsdb.String(50), nullable=False)
    patient = emidsdb.relationship('patient', backref='user')
    caregaps = emidsdb.relationship('caregaps', backref='user')

class patient(emidsdb.Model):
    patient_id = emidsdb.Column(emidsdb.Integer, primary_key=True)
    patient_name = emidsdb.Column(emidsdb.String(50), nullable=False)
    patient_gender = emidsdb.Column(emidsdb.String(20), nullable=False)
    patient_age = emidsdb.Column(emidsdb.Integer, nullable=False)
    patient_ethnicity = emidsdb.Column(emidsdb.String(50), nullable=False)
    patient_diagnosis = emidsdb.Column(emidsdb.String(50), nullable=False)
    primary_care_provider = emidsdb.Column(emidsdb.String(50), nullable=False)
    laboratory_results = emidsdb.Column(emidsdb.LargeBinary)
    hospital_id = emidsdb.Column(emidsdb.Integer, emidsdb.ForeignKey('hospital.hospital_id'))
    caregaps = emidsdb.relationship('caregaps', backref='user')

class caregaps(emidsdb.Model):
    care_id = emidsdb.Column(emidsdb.Integer, primary_key=True)
    care_name = emidsdb.Column(emidsdb.String(50), nullable=False)
    scheduled_date = emidsdb.Column(emidsdb.DateTime(timezone=True))
    hospital_id = emidsdb.Column(emidsdb.Integer, emidsdb.ForeignKey('hospital.hospital_id'))
    patient_id = emidsdb.Column(emidsdb.Integer, emidsdb.ForeignKey('patient.patient_id'))
    patient_name = emidsdb.Column(emidsdb.String(50), emidsdb.ForeignKey('patient.patient_name'))
    status = emidsdb.Column(emidsdb.String(10), nullable=False)


@app.route('/', methods=['POST','GET'])
def home():
    list_of_tables=['<h1 style="text-align: center;">Results</h1><br><br>']
    id = 1
    id = str(id)
    dt = datetime.datetime.now()
    dt = str(dt)
    print(dt)
    conn = sqlite3.connect('instance\emidsdb.sqlite3')
    # cursor = conn.cursor()
    # cursor.execute("select * from caregaps WHERE scheduled_date BETWEEN '2022-11-09' AND "+dt+" and status='NO'")
    # df = DataFrame(cursor.fetchall())
    # df.columns = cursor.keys()

    query = conn.execute("select * from caregaps WHERE scheduled_date BETWEEN '2022-11-09 10:20:00.987436' AND '"+dt+"' and status='NO'")
    cols = [column[0] for column in query.description]
    df = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

    print(df)

    df1 = df.select_dtypes(exclude=[float])
    df1 = df1.select_dtypes(exclude=[int])
    if request.method == 'POST':    
        search_str = request.form['search_string']
        if not search_str=='':
            result = BiGrams.GetScore(df1,search_str)      
            list_of_tables.append(result.to_html(classes='data', header="true"))
            list_of_tables.append('<br><br>')
        else:
            list_of_tables.append(df.to_html(classes='data', header="true"))
            list_of_tables.append('<br><br>')
    
    return render_template('emidshome.html', tables=list_of_tables)