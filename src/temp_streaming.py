from flask import Flask, render_template, Response
import cv2
from quick_capture_module import StreamCamera
import image_processing_module as ip
from constants import Camera_Settings
import time
from threading import Thread




app = Flask(__name__)

camera = None  


def gen_frames():
    base_height, base_width, _ = camera.capture().shape
    #video = cv2.VideoWriter("quick_capture_module_test_video.mp4", fourcc, Camera_Settings.FRAMERATE, (base_width, base_height), isColor=True)
    print(f"Recording with dimensions {base_width}x{base_height} with FPS {Camera_Settings.FRAMERATE}.")

    while True:
        image = camera.capture()

        # Normal lane detection.
        steering_angle_deg, lane_lines = ip.steering_info(image)
        image = ip.display_lanes_and_path(image, steering_angle_deg, lane_lines)
        #cv2.imshow("Quick Capture Module Unit Test - Auto Forward Lanes and Path", image)
        #lane_lines_len = len(lane_lines)

        # Print debugging while the camera is running decreases performance likely due to stdout buffering.
        # Print the entire thing on exit.
        # debug_output.append("Angle: " + str(steering_angle_deg - Drive_Params.STEERING_RACK_CENTER) + "\t" + (
        #     "No Lanes" if lane_lines_len == 0 
        #     else "One Lane: " + str(lane_lines[0]) if lane_lines_len == 1 
        #     else "Left Lane: " + str(lane_lines[0]) + " | Right Lane: " + str(lane_lines[1])
        # ))

        # Video
        image = cv2.resize(image, (base_width, base_height))
        buffer = cv2.imencode('.jpg',image)[1]
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        
        


        #video.write(image)

        # Exit upon pressing (q). Make sure the preview window is focused.
        # The 0xFF is a bitmask which makes it work with NumLock on.
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break



@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    camera = StreamCamera()
    app.run(host='192.168.2.208', port=3000, debug=False, threaded=True)
