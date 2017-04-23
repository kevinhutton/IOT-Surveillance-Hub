#IOT Surveillance Hub Backend

import os
import json
import urllib2
import common  
from flask import Flask,abort
from flask.ext.cors import CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return 'IOT Surveillance Hub Backend API'
@app.route('/admin/take_picture',methods=['GET','POST'])
def take_picture():
    return common.take_picture()

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

