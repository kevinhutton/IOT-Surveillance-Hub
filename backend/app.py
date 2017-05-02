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

@app.route('/')
def index():
    return 'IOT Surveillance Hub Backend API'

@app.route('/admin/take_picture',methods=['GET','POST'])
def take_picture():
    fileName = common.takeAndUploadPicture("manual")
    return json.dumps({'fileName': fileName, 'success': True})


# Takes pictures in a loop, uploading them as theyre taken.
# The loop stops 2 ways. 1) we hit the numPics limit. 2) a request is made to the /stop_picture_stream url by another http request
# while this request is still running, forcing this request to end early.
@app.route('/admin/start_picture_stream',methods=['GET','POST'])
def start_picture_stream():
    streamName = request.args.get("streamName")
    numPics = int(request.args.get("numPics"))
    millisDelayBetweenPics = int(request.args.get("millisDelayBetweenPics"))
    runTimeMillis = numPics * millisDelayBetweenPics
    filename = "cam-stream-%s.jpg" % streamName
    # hardcode pic file for now while testing.
    tmpFile = NamedTemporaryFile()
    filename = tmpFile.name
    outputFile = "/dev/null"


    # Tell camera to run for runTimeMillis, taking a pic every millisDelayBetweenPics, storing/overwriting the latest result into filename
    cmd = "raspistill -t %d -tl %d -o /tmp/img-increment.jpg -l %s -hf -vf -q 30 -w 640 -h 480" % (runTimeMillis, millisDelayBetweenPics, filename)
    # Make the command run as a background task, returning immediately, giving us the pid.
    # This way, we can loop and upload while it keeps taking more pictures in the background.
    bgTaskCommand = "%s > %s 2>&1 & echo $!" % (cmd, outputFile)
    raspPiStillCmdPid = common.shellExec(bgTaskCommand).strip()

    while True:

        # https://www.raspberrypi.org/documentation/raspbian/applications/camera.md
        # os.system("raspistill -t 6000 -tl 1000 -o /tmp/image_num_today.jpg -l %s -hf -vf -q 75 -w 640 -h 480 &" % filename)

        # os.system("raspistill -hf -vf -q 75 -w 640 -h 480 -o %s" % filename)
        # os.system("raspistill -hf -vf -o %s" % filename)
        time.sleep(millisDelayBetweenPics / 1000.0)

        # Check if the command is done, either by itself, or from being killed by another request.
        if not common.raspistillCommandIsRunning():
            break

        common.log("up "+filename)
        common.renameThenUploadPicture(filename, streamName)
        # common.uploadFile(filename)

    return json.dumps({'success': True, 'ret': raspPiStillCmdPid})

@app.route('/admin/stop_picture_stream',methods=['GET','POST'])
def stop_picture_stream():
    common.shellExec("kill $(ps aux | grep '[r]aspistill' | awk '{print $2}')")
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
    app.run(threaded=True)
    app.run(port=80)

