import os
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import Flask
cloudinary.config( 
  cloud_name = "kjh707", 
  api_key = "294731653526325", 
  api_secret = "XdEkW_0LTsf52PZPyhG3vn-P1YAa" 
)
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
@app.route('/admin/take_picture',methods=['GET','POST'])
def take_picture():
    filename = "pictures/cam.jpg"
    os.system("raspistill -o %s" % filename)
    jsonResponse = cloudinary.uploader.upload(filename)
    return json.dumps(jsonResponse)
if __name__ == '__main__':
    # Secret key to encrypt session variables
    app.debug = True
    app.run(port=80)

