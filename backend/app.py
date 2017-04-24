#IOT Surveillance Hub Backend

import os
import time
import json
import urllib2
import common
import requests
from flask import Flask,abort,request
from flask.ext.cors import CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

liveStreamRunState = {}

@app.route('/')
def index():
    return 'IOT Surveillance Hub Backend API'

@app.route('/admin/take_picture',methods=['GET','POST'])
def take_picture():
    return common.take_picture()

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
    filename = "C:/Users/IBM_ADMIN/Pictures/domestic-goat.jpg"
    numUploadFailures = 0
    maxUploadFailures = 3

    for x in range(0, numPics):
        # os.system("raspistill -o %s" % filename)
        time.sleep(millisDelayBetweenPics / 1000.0)

        # Check for a stop command sent in another request.
        if not liveStreamRunState[streamName]:
            break

        if 201 != uploadFile(filename=filename):
            numUploadFailures += 1
            # Allow a few failures, but if it fails too much, we abort.
            if numUploadFailures > maxUploadFailures:
                return json.dumps({'success': False})


    return json.dumps({'success': True})

@app.route('/admin/stop_picture_stream',methods=['GET','POST'])
def stop_picture_stream():
    global liveStreamRunState
    liveStreamRunState[request.args.get("streamName")] = False
    return json.dumps({'success': True})

def uploadFile(filename):
    files = {'upfile': open(filename, 'rb')}
    url = 'http://104.233.111.80/file-store/upload.php'
    resp = requests.post(url, files=files)
    return resp.status_code

# Determine the approxmate coordinates of this device via IP Gelocation
@app.route('/admin/geolocation',methods=['GET','POST'])
def geolocation():
    try:
	response = urllib2.urlopen('http://ip-api.com/json')
	data = json.load(response)
	return json.dumps(data)
    except:
	abort(404)

if __name__ == '__main__':
    app.debug = True
    app.run(port=80)

