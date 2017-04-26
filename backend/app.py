#IOT Surveillance Hub Backend

import os
import sys
import time
import json
import sqlite3
import urllib2
import traceback
from pprint import pprint
import common
import requests
from flask import Flask,abort,request,redirect
from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
from tempfile import NamedTemporaryFile

liveStreamRunState = {}

@app.route('/')
def index():
    return 'IOT Surveillance Hub Backend API'

@app.route('/admin/take_picture',methods=['GET','POST'])
def take_picture():
    cloudinaryResponse, fileName = common.takeAndUploadPicture("manual", True)
    return json.dumps(cloudinaryResponse)


# Takes pictures in a loop, uploading them as theyre taken.
# The loop stops 2 ways. 1) we hit the numPics limit. 2) a request is made to the /stop_picture_stream url by another http request
# while this request is still running, forcing this request to end early.
@app.route('/admin/start_picture_stream',methods=['GET','POST'])
def start_picture_stream():
    global liveStreamRunState
    liveStreamRunState[request.args.get("streamName")] = True
    numPics = int(request.args.get("numPics"))
    millisDelayBetweenPics = int(request.args.get("millisDelayBetweenPics"))
    streamName = request.args.get("streamName")
    filename = "cam-stream-%s.jpg" % streamName
    # hardcode pic file for now while testing.
    tmpFile = NamedTemporaryFile()
    filename = tmpFile.name

    for x in range(0, numPics):

        os.system("raspistill -hf -vf -o %s" % filename)
        time.sleep(millisDelayBetweenPics / 1000.0)

        # Check for a stop command sent in another request.
        if not liveStreamRunState[streamName]:
            break

        common.takeAndUploadPicture("live")


    return json.dumps({'success': True})

@app.route('/admin/stop_picture_stream',methods=['GET','POST'])
def stop_picture_stream():
    global liveStreamRunState
    liveStreamRunState[request.args.get("streamName")] = False
    return json.dumps({'success': True})



# Determine the approxmate coordinates of this device via IP Gelocation
@app.route('/admin/geolocation',methods=['GET','POST'])
def geolocation():
    try:
        response = urllib2.urlopen('http://ip-api.com/json')
        data = json.load(response)
        return json.dumps(data)
    except:
        abort(404)


@app.route('/admin/init_db',methods=['GET','POST'])
def initDb():
    common.initDb()
    return "ok"

@app.route('/api/notification-records',methods=['GET'])
def listNotificationRecords():
    records = common.getAllNotificationRecords()

    return json.dumps(records)

@app.route('/api/notification-records',methods=['POST'])
def createNotificationRecord():
    recordId = common.createNotificationRecord(
        request.form.get("email"),
        request.form.get("startDate"),
        request.form.get("endDate"),
        request.form.get("dailyStartTime"),
        request.form.get("dailyEndTime"),
        request.form.get("throttleMinutes")
    )
    return json.dumps({'id': recordId})

@app.route('/api/notification-records/<id>',methods=['PUT'])
def updateNotificationRecord(id):
    if request.form.has_key("disabled"):
        common.updateNotificationRecord(id, request.form.get("disabled"))

    return json.dumps({'success': True})

@app.route('/api/notification-records/<id>',methods=['DELETE'])
def deleteNotificationRecord(id):
    common.deleteNotificationRecord(id)
    return json.dumps({'success': True})

@app.route('/admin/tttt',methods=['GET'])
def tttt():
    sql = """
        select CURRENT_TIMESTAMP dt, 
        DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME') ldt, 
        strftime('%H:%M', DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')) lt, 
        *
          from Notifications
    """
    # for r in common.query(sql):
    #     pprint(r)
    # common.log("")
    common.notifySubscribersOfCameraActivity()
    return json.dumps({'success': True})

@app.route('/admin/test-email',methods=['GET'])
def testEmail():
    common.sendNotificationEmail("rehfeldchris@gmail.com", "motion-detected")
    return json.dumps({'success': True})


if __name__ == '__main__':
    app.debug = True
    app.run(port=80)

