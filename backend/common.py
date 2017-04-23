import os
import json
import urllib2
import cloudinary
import cloudinary.uploader
import cloudinary.api
from tempfile import NamedTemporaryFile

cloudinary.config(
    cloud_name="kjh707",
    api_key="294731653526325",
    api_secret="XdEkW_0LTsf52PZPyhG3vn-P1YA"
)


def take_picture(tag=None):
    tmpFile = NamedTemporaryFile()
    os.system("raspistill -hf -o %s" % tmpFile.name)
    jsonResponse = cloudinary.uploader.upload(
        tmpFile.name, tag="motion-detected")
    tmpFile.close()
    return json.dumps(jsonResponse)
