import os
import json
import urllib2
import cloudinary
import cloudinary.uploader
import cloudinary.api
import sqlite3
from tempfile import NamedTemporaryFile

cloudinary.config(
    cloud_name="kjh707",
    api_key="294731653526325",
    api_secret="XdEkW_0LTsf52PZPyhG3vn-P1YA"
)
dbLocation = '/var/lib/iot-project/iot-project.db'


def take_picture(tag=None):
    tmpFile = NamedTemporaryFile()
    os.system("raspistill -hf -vf -o %s" % tmpFile.name)
    jsonResponse = cloudinary.uploader.upload(
        tmpFile.name, tag="motion-detected")
    tmpFile.close()
    return json.dumps(jsonResponse)

def createBluetoothDevicesTable():
    conn = sqlite3.connect(dbLocation)
    print "Opened database successfully";
    conn.execute('''CREATE TABLE BluetoothDevices 
	       (MAC           TEXT PRIMARY KEY    NOT NULL,
	       DEVICENAME     TEXT     NOT NULL,
	       TIMESTAMP DATETIME)''')
    print "Table created successfully";
    conn.close()

def createNotificationsTable():
    conn = sqlite3.connect(dbLocation)
    print "Opened database successfully";
    conn.execute('''CREATE TABLE Notifications 
	       (ID INT PRIMARY KEY     NOT NULL,
	       email           TEXT    NOT NULL)''')
    print "Table created successfully";
    conn.close()

def query(queryString):
    conn = sqlite3.connect(dbLocation)
    c = conn.execute(queryString)
    result = c.fetchall()
    conn.commit()
    conn.close()
    return result
