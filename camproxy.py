import requests
from flask import Flask, Response, stream_with_context
import ephem
import random
from datetime import datetime
from datetime import timedelta
import shutil
import time
import threading
import os

USER = os.environ.get('CAMUSER')
PASS = os.environ.get('CAMPASS')
HOST = os.environ.get('CAMHOST')

app = Flask(__name__, static_url_path='/home/pi/')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/cam1.jpg')
def cam1():
    return app.send_static_file('cam1.jpg')

@app.route('/cam2.jpg')
def cam2():
    return app.send_static_file('cam2.jpg')

@app.route('/cam3.jpg')
def cam3():
    return app.send_static_file('cam3.jpg')

@app.route('/cam4.jpg')
def cam4():
    return app.send_static_file('jupiter.jpg')

def getImg(channel):

    try:
        os.remove('/tmp/static/temp.jpg')
    except:
        pass

    url = 'http://%s/ISAPI/Streaming/channels/%s01/picture' % (CAMHOST, channel)
    try:
        req = requests.get(url, auth=(USER, PASS))
        with open('/tmp/static/temp.jpg', 'wb') as f:
            f.write(req.content)
    except:
        return
    else:
        shutil.copyfile('/tmp/static/temp.jpg', '/tmp/static/cam%s.jpg' % str(channel))

def jupiterImageUpdater():

    nextJupiter = datetime.utcnow()
    nextWestbrook = nextJupiter

    while(True):

        now = datetime.utcnow()
        if (now >= nextJupiter):
            nextJupiter = now + timedelta(minutes=5)
            imagenum = 2

            local = ephem.Observer()
            local.lat = '26.938'
            local.lon = '-80.070'
            local.horizon = '-12'
            local.epoch=now
            sun = ephem.Sun()
            sun.compute(local)

            if (sun.alt > 0):
                imagenum = random.choice([2, 8, 16])
            else:
                imagenum = random.choice([2, 20])

            try:
                os.remove('/tmp/static/temp.jpg')
            except:
                pass

            try:
                url = "https://video-monitoring.com/beachcams/jupiter/latest.json"
                req = requests.get(url)

                images = req.json()
                url = "https://video-monitoring.com/beachcams/jupiter/" + images["s" + str(imagenum)]["mr"]

                req = requests.get(url)
                with open('/tmp/static/temp.jpg', 'wb') as f:
                    f.write(req.content)
            except:
                next
            else:
                shutil.copyfile('/tmp/static/temp.jpg', '/tmp/static/jupiter.jpg')
        elif (now >= nextWestbrook):

            try:
                getImg(1)
                getImg(2)
                getImg(3)
            except:
                next

            nextWestbrook = now + timedelta(seconds=8)
        else:
            time.sleep(2)
                

if __name__ == '__main__':
    try:
        shutil.os.mkdir('/tmp/static/')
    except:
        pass
    shutil.copyfile('/home/pi/index.html', '/tmp/static/index.html')
    t = threading.Thread(target=jupiterImageUpdater)
    t.daemon = True
    t.start()
    app.run(threaded=True)

