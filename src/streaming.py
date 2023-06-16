"""
Streaming to web server.
"""

from flask import Flask, render_template, Response
import numpy as np
import cv2

# Package Imports
from image_processing_module import zero_image
app = Flask(__name__)
yield_val 


def gen_frames():
    global image
    print("Streaming.")

    while True:
        if image is None:
            image_copy = np.zeros((10 ,10 ,3), np.uint8)
        else:
            image_copy = image.copy()
        buffer = cv2.imencode('.jpg', image_copy)[1]
        frame = buffer.tobytes()
        yield (b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n") # Concatenate frame one by one and show result.
@app.route('/video_feed')
def video_feed():
    global image
    return Response(gen_frames(image), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

app.run(host='192.168.2.208', port=3000, debug=False, threaded=True)