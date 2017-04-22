#IOT Surveillance Hub Backend

import os
import json
import urllib2
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import Flask,abort
from flask.ext.cors import CORS
cloudinary.config( 
  cloud_name = "kjh707", 
  api_key = "294731653526325", 
  api_secret = "XdEkW_0LTsf52PZPyhG3vn-P1YA" 
)
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return 'IOT Surveillance Hub Backend API'
@app.route('/admin/take_picture',methods=['GET','POST'])
def take_picture():
    filename = "/tmp/cam.jpg"
    os.system("raspistill -hf -o %s" % filename)
    jsonResponse = cloudinary.uploader.upload(filename)
    return json.dumps(jsonResponse)

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

