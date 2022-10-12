import picamera
from time import sleep

camera = picamera.PiCamera()
#lasspicamera.PiOverlayRenderer(parent, source, resolution=None, format=None, layer=0, alpha=255, fullscreen=True, window=None, crop=None, rotation=0, vflip=False, hflip=False)
#camera.resolution = (1280, 720)
#camera.fullscreen = False
#camera.window = (0,0,100,100)
camera.start_preview(alpha=200)  
sleep(2)
#camera.capture('/home/pi/Desktop/image.jpg')
#camera.stop_preview()

#self._init_camera(camera_num, stereo_mode, stereo_decimate)
#camera.capture('example.jpg')

#camera.capture('example2.jpg')

#camera.start_recording('examplevid.h264')
#time.sleep(1)
#camera.stop_recording()

#sleep(5)

for i in range (2):
    fstring = f'test{i}.jpg'
    camera.capture(fstring)


camera.stop_preview()
