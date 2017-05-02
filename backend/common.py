import os
import time
import json
import datetime
import sys
import urllib
import urllib2
import traceback
import smtplib
from pprint import pprint
import cloudinary
import cloudinary.uploader
import cloudinary.api
import sqlite3
import requests
from flask import Flask,abort,request,redirect
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import PIPE, Popen


from tempfile import NamedTemporaryFile

cloudinary.config(
    cloud_name="kjh707",
    api_key="294731653526325",
    api_secret="XdEkW_0LTsf52PZPyhG3vn-P1YA"
)
# dbLocation = 'iot-project.db'
dbLocation = '/var/lib/iot-project/iot-project.db'
mockEmailSend = False
# mockEmailSend = True
urlRoot = "https://kevinhutton.github.io/IOT-Project/"

def shellExec(command):
    process = Popen(args=command, stdout=PIPE, shell=True)
    return process.communicate()[0]

def raspistillCommandIsRunning():
    return bool(shellExec("ps aux | grep '[r]aspistill' | awk '{print $2}'").strip())

# uploads to both cloudinary and the homebrew place.
# this way we can search for it later via the homebrew.
def takeAndUploadPicture(tag):
    tmpFile = NamedTemporaryFile()
    # We set the timout to 500ms, which results in a poorly exposed image. But, we do this to make it take a pic as fast as possible.
    # 1500ms gives a better pic. We also use a low quality -q setting to keep the file size small, so uploads / downloads are speedy.
    os.system("raspistill --nopreview --timeout 500 -hf -vf -q 35 -w 1024 -h 768 -o %s" % tmpFile.name)
    fileNameWithTag = renameThenUploadPicture(tmpFile.name, tag)
    tmpFile.close()
    now = datetime.datetime.now()
    nearBy = datetime.datetime.now() - datetime.timedelta(hours = 8)
    ymd24 = now.strftime("%Y-%m-%d %H:%M:%S")
    ymd24NearBy = nearBy.strftime("%Y-%m-%d %H:%M:%S")
    fileInfo = {'fileNameWithPath': fileNameWithTag, 'fileName' : os.path.basename(fileNameWithTag), 'dateTime': ymd24, 'dateTimeNearBy': ymd24NearBy}
    return fileInfo

def renameThenUploadPicture(fileName, tag):
    fileNameWithTag = "/tmp/%s-%s.jpg" % (tag, time.time())
    os.system("cp %s %s" % (fileName, fileNameWithTag))
    uploadFile(fileNameWithTag)
    os.system("rm -f %s" % fileNameWithTag)
    return fileNameWithTag

def createBluetoothDevicesTable():
    conn = sqlite3.connect(dbLocation)
    print "Opened database successfully"
    conn.execute('''CREATE TABLE BluetoothDevices 
	       (MAC           TEXT PRIMARY KEY    NOT NULL,
	       DEVICENAME     TEXT     NOT NULL,
	       TIMESTAMP DATETIME)''')
    print "Table created successfully"
    conn.close()

def createNotificationHistoryTable():
    conn = sqlite3.connect(dbLocation)
    print "Opened database successfully"
    conn.execute('''
           CREATE TABLE NotificationHistory (
               email           TEXT NOT NULL,
               dateSent        DATETIME,
               PRIMARY KEY (email, dateSent)
           )
    ''')
    print "Table created successfully"
    conn.close()

def createNotificationsTable():
    conn = sqlite3.connect(dbLocation)
    print "Opened database successfully"
    conn.execute('''
           CREATE TABLE Notifications (
               email           TEXT NOT NULL,
               startDate       DATETIME,
               endDate         DATETIME,
               dailyStartTime  TEXT,
               dailyEndTime    TEXT,
               throttleMinutes INT NOT NULL,
               disabled        INT NOT NULL
           )
    ''')
    print "Table created successfully"
    conn.execute('''
           CREATE INDEX Notifications_startDate_endDate on Notifications (startDate, endDate)
    ''')
    print "Index created successfully"
    conn.close()

def getConnection():
    conn = sqlite3.connect(dbLocation)
    conn.row_factory = dict_factory
    return conn

def dropAllTables():
    conn = getConnection()
    cur = conn.cursor()
    tables = list(cur.execute("select name from sqlite_master where type is 'table'"))
    cur.executescript(';'.join(["""drop table if exists "%s" """ % i['name'] for i in tables]))
    conn.close()

def initDb():
    dropAllTables()
    createBluetoothDevicesTable()
    createNotificationHistoryTable()
    createNotificationsTable()

def query(queryString):
    conn = getConnection()
    c = conn.execute(queryString)
    result = c.fetchall()
    conn.commit()
    conn.close()
    return result

def executeWithArgs(sql, args=None):
    conn = getConnection()
    if args == None:
        c = conn.execute(sql)
    else:
        c = conn.execute(sql, args)
    conn.commit()
    conn.close()
    return c.lastrowid

def selectAllWithArgs(sql, args=None):
    conn = getConnection()
    if args == None:
        c = conn.execute(sql)
    else:
        c = conn.execute(sql, args)
    result = c.fetchall()
    conn.commit()
    conn.close()
    return result

def getAllNotificationRecords():
    sql = """
        select rowid, *
          from Notifications
    """

    return selectAllWithArgs(sql)

def getCurrentlyActiveNotificationRecords():
    # We store the dates and times in local time.
    sql = """
        select rowid, CURRENT_TIMESTAMP dt, strftime('%H:%M', DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')) lt, *
          from Notifications
         where (startDate      = '' or startDate      <= DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME'))
           and (endDate        = '' or endDate        >= DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME'))
           and (dailyStartTime = '' or dailyStartTime <= strftime('%H:%M', DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')))
           and (dailyEndTime   = '' or dailyEndTime   >= strftime('%H:%M', DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')))
           and disabled = 0
    """

    # We only return 1 record per user, because a user might have some temporarily overlapping notification records setup.
    # It should be the one with the smallest throttleMinutes value.
    noDupeDict = {}
    for row in selectAllWithArgs(sql):
        if not row['email'] in noDupeDict or noDupeDict[row['email']]['throttleMinutes'] < row['throttleMinutes']:
            noDupeDict[row['email']] = row

    noDupeList = []
    for k in noDupeDict.keys():
        noDupeList.append(noDupeDict[k])

    return noDupeList

def createNotificationRecord(email, startDate, endDate, dailyStartTime, dailyEndTime, throttleMinutes):
    sql = """
    insert 
      into Notifications 
           (email, startDate, endDate, dailyStartTime, dailyEndTime, throttleMinutes, disabled)
    values 
           (?, ?, ?, ?, ?, ?, 0)
    """

    return executeWithArgs(sql, (email, startDate, endDate, dailyStartTime, dailyEndTime, throttleMinutes))

def updateNotificationRecord(id, disabled):
    sql = """
    update Notifications 
       set disabled = ?
     where rowid = ?
    """

    return executeWithArgs(sql, (disabled, id))

def deleteNotificationRecord(id):
    sql = """
    delete 
      from Notifications 
     where rowid = ?
    """

    executeWithArgs(sql, (id,))

def log(msg):
    sys.stdout.write(msg)
    sys.stdout.write("\n")
    sys.stdout.flush()

def recordEmailSent(email):
    sql = """
    insert into NotificationHistory 
    (email, dateSent)
    values 
    (?, CURRENT_TIMESTAMP)
    """

    return executeWithArgs(sql, (email,))

def sendNotificationEmail(email, fileInfo):
    if mockEmailSend:
        log("pretending to send email to: " + email)
        return True
    else:
        log("sending email to: " + email)
        messageHtml = """
        Camera activity detected. <br>
        <a href="%s#live">View Camera Live</a> <br>
        <a href="%s?tag=%s&submit=1#search-pictures">View Image That Triggered Alert</a> <br>
        <a href="%s?tag=%s&searchStartDate=%s&submit=1#search-pictures">View All Images Taken Near The Trigger %s</a> <br>
        
        """ % (
            urlRoot,
            urlRoot, urllib.quote_plus(fileInfo['fileName']),
            urlRoot, urllib.quote_plus("motion-detected"), urllib.quote_plus(fileInfo['dateTimeNearBy']), fileInfo['dateTimeNearBy'])
        sender = 'iot-camera-activity-notifier-no-reply@example.com'
        params = {'subject': "IOT Surveillance Hub Activity Detected", 'from': sender, 'to': email, 'message': messageHtml}
        url = 'http://104.233.111.80/file-store/email.php'
        requests.get(url, params=params)
        return True

def emailHasNotBeenEmailedTooRecently(email, minimumMinutes):
    sql = """
    select count(*) cnt
      from NotificationHistory 
     where email = ?
       and dateSent > datetime('now', '-%d Minute')
    """ % minimumMinutes

    return selectAllWithArgs(sql, (email,))[0]['cnt'] == 0

# We can call this method whenever the camera detects activity. It will send any needed notifications.
def notifySubscribersOfCameraActivity(fileInfo):
    for row in getCurrentlyActiveNotificationRecords():
        if emailHasNotBeenEmailedTooRecently(row['email'], row['throttleMinutes']):
            if sendNotificationEmail(row['email'], fileInfo):
                recordEmailSent(row['email'])

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def uploadFile(filename):
    files = {'upfile': open(filename, 'rb')}
    url = 'http://104.233.111.80/file-store/upload.php'
    resp = requests.post(url, files=files)
    return resp.status_code