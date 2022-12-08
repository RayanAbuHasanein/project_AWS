from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from flask import json
import pymysql
from werkzeug.utils import secure_filename
# from flask_mysqldb import MySQL
import mysql.connector
from array import *

global memcache

app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')

memcache = {}

# array1 = array []

db = pymysql.connect(host='database-2.cbnbjo3bjf2p.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='cloud!!11',
                            database='DB',
                            )

cursor = db.cursor()
value = ""
count = 0 

################## SEARCH  ###############################
hit = 0 
miss = 0 
hit_rate = 0 
miss_rate = 0 
len = hit+miss
@app.route('/get', methods=['POST'])
def get():
    # sql = "DELETE FROM memory"
    # cursor.execute(sql)
    # db.commit()
    global len
    global hit
    global miss
    global miss_rate
    global hit_rate
    key = request.form.get('key')

    if key in memcache:
        value = memcache[key]
        count = 1
        print(memcache.keys())
        hit=hit+1
        len=len+1
        hit_rate=hit/len
        val=(len,hit_rate)
        sql = "INSERT INTO memory (req,hit_rate) VALUES (%s,%s)"
        cursor.execute(sql,val)
        db.commit()
        # sql = "UPDATE memory SET req = (%s) WHERE 1=1"
        # cursor.execute(sql,len)
        # db.commit()

    else:
        sql = "SELECT photo FROM cloud WHERE keyy = (%s)"
        cursor.execute(sql,key)
        db.commit()
        value = cursor.fetchall()
        memcache[key]= value
        count = 0 
        # len=len+1
        miss=miss+1
        len=hit+miss
        miss_rate=miss/len
        val=(len,miss_rate)
        sql = "INSERT INTO memory (req,miss_rate) VALUES (%s,%s)"
        cursor.execute(sql,val)
        db.commit()
    return render_template("Search.html", res = value[0][0], c = count)

################## LIST  #################################

@app.route('/list', methods=['POST'])
def list():
    sql = "SELECT keyy FROM cloud"
    cursor.execute(sql)
    value = cursor.fetchall()
    return render_template("ShowKeys.html", value=value)

################ CLEAR KEYS & PICS ######################

@app.route('/clear', methods=['POST'])
def clear():
    sql = "DELETE FROM cloud"
    cursor.execute(sql)
    db.commit()
    return render_template("ShowKeys.html")


################## UPLOAD PHOTO ########################

@app.route('/upload', methods=['POST'])
def upload():
    key = request.form.get('key')
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join("C:/Users/HP/Desktop/cloud/static",filename))
    sql = "INSERT INTO cloud (photo,keyy) VALUES (%s,%s)"
    val = (filename, key)
    cursor.execute(sql,val)
    db.commit()
    response = app.response_class(
        response = json.dumps("Added successfully "),
        status = 200, 
        mimetype ='application/json')
    return response

################## DROP A KEY ######################

@app.route('/drop', methods=['POST'])
def drop():
    value = "Record(s) deleted "
    key = request.form.get('key')
    sql = "DELETE FROM cloud WHERE keyy = (%s)"
    cursor.execute(sql,key)
    db.commit()
    return render_template("UploadPhoto.html", value= value)


################## MEMORY CONFIG #####################

@app.route('/config_req', methods=['POST'])
def config_req():
        sql = "SELECT req FROM memory"
        cursor.execute(sql)
        value = cursor.fetchone()
        return render_template("ShowMemoryCache.html", value=value)

@app.route('/config_hit', methods=['POST'])
def config_hit():
        sql = "SELECT hit_rate FROM memory"
        cursor.execute(sql)
        value1 = cursor.fetchone()
        return render_template("ShowMemoryCache.html", value1=value1)

@app.route('/config_miss', methods=['POST'])
def config_miss():
        sql = "SELECT miss_rate FROM memory"
        cursor.execute(sql)
        value2 = cursor.fetchone()
        return render_template("ShowMemoryCache.html", value2=value2)


################## ROUTE ##########################
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/search")
def search():
    return render_template("Search.html")

@app.route("/showKeys")
def showKeys():
    return render_template("ShowKeys.html")

@app.route('/uploading')
def uploading():
    return render_template("UploadPhoto.html")

@app.route("/showMemoryCache")
def showMemoryCache():
    return render_template("showMemoryCache.html")
if __name__ == "__main__":
    app.run()