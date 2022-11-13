import os
import sqlite3
from flask import Flask, jsonify, json, render_template,request, send_file,redirect,url_for
import pandas as pd
from werkzeug.utils import secure_filename
from markupsafe import escape
from werkzeug.security import safe_join
import numpy as np
import glob
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import calendar

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

class patient(emidsdb.Model):
    patient_name = emidsdb.Column(emidsdb.String(50), nullable=False)
    patient_mobile_number = emidsdb.Column(emidsdb.String(13), nullable=False)
    patient_gender = emidsdb.Column(emidsdb.String(20), nullable=False)
    patient_age = emidsdb.Column(emidsdb.Integer, nullable=False)
    patient_ethnicity = emidsdb.Column(emidsdb.String(50), nullable=False)
    patient_diagnosis = emidsdb.Column(emidsdb.String(50), nullable=False)
    entered_date = emidsdb.Column(emidsdb.DateTime(timezone=True), primary_key=True)
    primary_care_provider = emidsdb.Column(emidsdb.String(50), nullable=False)
    laboratory_results = emidsdb.Column(emidsdb.LargeBinary)
    hospital_id = emidsdb.Column(emidsdb.Integer, nullable=False)

class caregaps(emidsdb.Model):
    care_id = emidsdb.Column(emidsdb.Integer, primary_key=True)
    care_name = emidsdb.Column(emidsdb.String(50), nullable=False)
    care_type = emidsdb.Column(emidsdb.String(50), nullable=False)
    patient_mobile_number = emidsdb.Column(emidsdb.String(13), nullable=False)
    patient_name = emidsdb.Column(emidsdb.String(50), nullable=False)
    scheduled_date = emidsdb.Column(emidsdb.DateTime(timezone=True))
    score = emidsdb.Column(emidsdb.Integer, nullable=False)
    hospital_id = emidsdb.Column(emidsdb.Integer, nullable=False)
    status = emidsdb.Column(emidsdb.String(10), nullable=False)




@app.route('/', methods=['POST','GET'])
def home():

    list=[]
    id = 1
    id = str(id)
    dt = datetime.datetime.now()
    dt = str(dt)
    conn = sqlite3.connect('emidsdb.sqlite3')
    query = conn.execute("select * from caregaps WHERE status='Missed'")
    cols = [column[0] for column in query.description]
    df = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
    print("Hiii")
    # print(df)
    df1 = df.select_dtypes(exclude=[float])
    df1 = df1.select_dtypes(exclude=[int])
    result=df1
    if request.method == 'POST':  
        option = request.form.getlist('app_type')
        categ = option[0]
        search_str = request.form['search_string']
        if not search_str=='':
            result = BiGrams.GetScore(df1,search_str)                  
        else:
            pass        
        list= result.values.tolist()
        print(list)
        new_list=[]
        if categ=='Appointment':
            for cg in list:
                if cg[1] == categ:
                    new_list.append(cg)
        elif categ=='Lab Test':
            for cg in list:
                if cg[1] == categ:
                    new_list.append(cg)
        elif categ=='Vaccination':
            for cg in list:
                if cg[1] == categ:
                    new_list.append(cg)
        elif categ=='Surgery':
            for cg in list:
                if cg[1] == categ:
                    new_list.append(cg)
        else:
            new_list=list

        list=new_list

        for i in list:
            l1 = i[4].split(' ')
            datetime_str = l1[0]
            print(datetime_str)
            datetime_object = datetime.datetime.strptime(datetime_str, '%Y-%m-%d')
            month = datetime_object.strftime("%b")
            date = datetime_object.strftime("%d")
            time = datetime_object.strftime("%H:%M %p")
            i[4] = [month,date,time]
        
    else:
        list= result.values.tolist()
        for i in list:
            l1 = i[4].split(' ')
            datetime_str = l1[0]
            print(datetime_str)
            datetime_object = datetime.datetime.strptime(datetime_str, '%Y-%m-%d')
            month = datetime_object.strftime("%b")
            date = datetime_object.strftime("%d")
            time = datetime_object.strftime("%H:%M %p")
            i[4] = [month,date,time]

    return render_template('emidshome.html', your_list = list)

@app.route('/profile/<string:Patient>')
def profile(Patient):
    Patient = patient.query.filter_by(patient_name=Patient).first()
    if Patient == None:
        # flash('User %s not found.' % nickname)
        return redirect(url_for('home'))

    conn = sqlite3.connect('emidsdb.sqlite3')
    cursor = conn.cursor()
    name = str(Patient.patient_name)
    cursor.execute("select * from caregaps WHERE patient_name = '" + name + "' and status = 'Missed'")
    df = DataFrame(cursor.fetchall())

    cursor.execute("select * from caregaps WHERE patient_name = '" + name + "' and status = 'Pending'")
    df1 = DataFrame(cursor.fetchall())

    cursor.execute("select * from caregaps WHERE patient_name = '" + name + "' and status = 'Completed'")
    df2 = DataFrame(cursor.fetchall())
    # df.columns = cursor.keys()
    # df1 = df.select_dtypes(exclude=[float])
    # df1 = df1.select_dtypes(exclude=[int])
    care_gaps=df.values.tolist()    
    pending_tests = df1.values.tolist()
    completed_tests = df2.values.tolist()
    for gap in care_gaps:
        l1 = gap[5].split(' ')
        gap[5] = l1[0]
    for gap in pending_tests:
        l1 = gap[5].split(' ')
        gap[5] = l1[0]
    for gap in completed_tests:
        l1 = gap[5].split(' ')
        gap[5] = l1[0]
    print(care_gaps)
    biodata=[Patient.patient_name,Patient.patient_ethnicity,Patient.patient_mobile_number,"13/03/2003",Patient.patient_gender,Patient.primary_care_provider]
    return render_template('profile.html', data=[biodata,care_gaps,pending_tests,completed_tests])

@app.route('/profiles',methods=['POST','GET'])
def profiles():
    conn = sqlite3.connect('emidsdb.sqlite3')
    cursor = conn.cursor()    
    cursor.execute("select patient_name, patient_mobile_number from patient")
    df = DataFrame(cursor.fetchall())
    data=df.values.tolist()
    result=df
    if request.method == 'POST':    
        search_str = request.form['search_string']
        if not search_str=='':
            result = BiGrams.GetScore(df,search_str)                  
        else:
            pass

        data= result.values.tolist()                
    else:
        data= result.values.tolist()        

    return render_template('allprofiles.html',data=data)

@app.route('/patientdetails', methods=['POST','GET'])
def patient_details():
    if request.method == 'POST':
        name = request.form['name']
        phno = request.form['phno']
        age = request.form['age']
        gender = request.form['gender']
        etnicity = request.form['ethnicity']
        diagnosis = request.form['diagnosis']
        careprovider = request.form['careprovider']
        date = datetime.datetime.now()
        labresults = request.files['labresults']
        hospitalid = 1
        details = patient(patient_name=name, patient_mobile_number =phno, patient_gender=gender, patient_age=age, patient_ethnicity=etnicity, patient_diagnosis=diagnosis, entered_date=date, primary_care_provider=careprovider, laboratory_results=labresults.read(), hospital_id=hospitalid)
        emidsdb.session.add(details)
        emidsdb.session.commit()
        return render_template('submit.html')
    return render_template('patient_details.html')


chronic_diseases_list = ['cancer', 'heart disease', 'stroke', 'diabetes', 'alzheimer', 'epilepsy', 'als', 'asthama', 'osteoporosis','sugar','blood pressure']
care_type_dict = {'surgery': 200, 'lab test': 75, 'vaccination': 75, 'appointment':55}
def get_score(diagnosis_name, care_type):
    score = 0
    diagnosis_name = diagnosis_name.lower()
    care_type= care_type.lower()
    if diagnosis_name in chronic_diseases_list:
        score+=20
    score+=care_type_dict[care_type]
    return score


@app.route('/caregapdetails', methods=['POST','GET'])
def caregap_details():
    if request.method == 'POST':
        patientname = request.form['patientname']
        phno = request.form['phno']
        caretype = request.form['caretype']
        diagnosis = request.form['diagnosis']
        scheduleddate = request.form['scheduleddate']
        scheduleddate = datetime.datetime.strptime(scheduleddate, '%Y-%m-%d')
        hospitalid = 1
        status = "Completed"
        score = get_score(diagnosis, caretype)
        details = caregaps(patient_name=patientname, patient_mobile_number =phno, care_type=caretype,  care_name=diagnosis, scheduled_date=scheduleddate, hospital_id=hospitalid, status=status, score=score)
        emidsdb.session.add(details)
        emidsdb.session.commit()
        return render_template('submit.html')
    return render_template('caregap_details.html')