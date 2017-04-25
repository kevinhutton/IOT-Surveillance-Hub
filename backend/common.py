import os
import json
import sys
import urllib2
import traceback
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
# dbLocation = 'iot-project.db'
dbLocation = '/var/lib/iot-project/iot-project.db'


def take_picture(tag=None):
    tmpFile = NamedTemporaryFile()
    os.system("raspistill -hf -o %s" % tmpFile.name)
    jsonResponse = cloudinary.uploader.upload(
        tmpFile.name, tag="motion-detected")
    tmpFile.close()
    return json.dumps(jsonResponse)

def createBluetoothDevicesTable():
    conn = sqlite3.connect(dbLocation)
    print "Opened database successfully"
    conn.execute('''CREATE TABLE BluetoothDevices 
	       (ID INT PRIMARY KEY     NOT NULL,
	       MAC           TEXT    NOT NULL,
	       DEVICENAME          TEXT     NOT NULL,
	       DEVICETYPE       TEXT)''')
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

def dropAllTables():
    conn = sqlite3.connect(dbLocation)
    cur = conn.cursor()
    tables = list(cur.execute("select name from sqlite_master where type is 'table'"))
    cur.executescript(';'.join(["drop table if exists %s" %i for i in tables]))
    conn.close()

def initDb():
    dropAllTables()
    createBluetoothDevicesTable()
    createNotificationHistoryTable()
    createNotificationsTable()

def query(queryString):
    conn = sqlite3.connect(dbLocation)
    conn.row_factory = dict_factory
    c = conn.execute(queryString)
    result = c.fetchall()
    conn.commit()
    conn.close()
    return result

def getAllNotificationRecords():
    sql = """
        select rowid, *
          from Notifications
    """

    return query(sql)

def getCurrentlyActiveNotificationRecords():
    sql = """
        select rowid, *
          from Notifications
         where (startDate      is null or startDate >= CURRENT_TIMESTAMP)
           and (endDate        is null or endDate <= CURRENT_TIMESTAMP)
           and (dailyStartTime is null or dailyStartTime >= strftime('%H:%M', CURRENT_TIMESTAMP))
           and (dailyEndTime   is null or dailyEndTime <= strftime('%H:%M', CURRENT_TIMESTAMP))
    """
    return query(sql)

def createNotificationRecord(email, startDate, endDate, dailyStartTime, dailyEndTime, throttleMinutes):
    conn = sqlite3.connect(dbLocation)
    log('open')
    sql = """
    insert into Notifications 
    (email, startDate, endDate, dailyStartTime, dailyEndTime, throttleMinutes, disabled)
    values 
    (?, ?, ?, ?, ?, ?, 0)
    """
    # c = conn.execute(sql, ("", "", "", "", "", "11"))
    c = conn.execute(sql, (email, startDate, endDate, dailyStartTime, dailyEndTime, throttleMinutes))
    log( "exec")

    conn.commit()
    conn.close()
    log(str(c.lastrowid))

    return c.lastrowid

def updateNotificationRecord(id, disabled):
    conn = sqlite3.connect(dbLocation)
    sql = """
    update Notifications 
      set disabled = ?
    where rowid = ?
    """
    c = conn.execute(sql, (disabled, id))
    conn.commit()
    conn.close()

def deleteNotificationRecord(id):
    conn = sqlite3.connect(dbLocation)
    sql = """
    delete 
      from Notifications 
     where rowid = ?
    """
    c = conn.execute(sql, (id))
    conn.commit()
    conn.close()

def log(msg):
    sys.stdout.write(msg)
    sys.stdout.write("\n")
    sys.stdout.flush()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
