"""
From ancabilloni/udp_camera_streaming. https://github.com/ancabilloni/udp_camera_streaming
"""
# Package imports
from threading import Thread
from struct import pack
import socket
import cv2
import math

# Local imports
from constants import Streaming
from camera import Camera

class FrameSegment:
    """
    Object to break down image frame segment.
    if the size of image exceed maximum datagram size.
    """
    MAX_DGRAM = 2 ** 16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # Extract 64 bytes in case UDP frame overflow.
    def __init__(self, sock, port, addr="127.0.0.1"):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """ 
        Compress image and break down into data segments.
        """
        compress_img = cv2.imencode('.jpg', img)[1]
        dat = compress_img.tostring()
        size = len(dat)
        count = math.ceil(size / (self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(pack("B", count) + dat[array_pos_start:array_pos_end], (self.addr, self.port))
            array_pos_start = array_pos_end
            count -= 1

    
class Streamer():

   
    streaming_enabled = Streaming.ENABLED
    
    def __init__(self):

        #self.camera = Camera()
        #self.frame = self.camera.read() # need an initial frame so udp_frame() doesn't throw error
        
        self.thread = Thread(target=self._send, args = ()) # Could make the switch to TCP now that this is threaded. RTSP would be really cool but streaming isn't a priority right now
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.port = Streaming.DESTINATION_PORT
        self.addr = Streaming.DESTINATION_ADDRESS
        self.frame_segment = FrameSegment(self.server_socket, self.port, self.addr)
        self.threaded = False
        self.stopped = False
        
        if not self.streaming_enabled:
            print("Streaming is disabled. See config.yml to enable.")
        

    def stream_image(self, image):
        self.frame=image
        if not self.threaded:
            self.frame_segment.udp_frame(image)

    def _send(self):
        while not self.stopped:
            if self.streaming_enabled:
                self.frame_segment.udp_frame(self.frame)
            else:
                pass

    # Enables threaded mode for the Streamer. This seemed to have been working fine but then I started seeing weird
    # controller behavior (see chris_notes.md). For now, you can just not call the start method, and the Streamer will operate in the thread wherein it was instantiated.
    # Note: Whether or not the Streamer thread has started, you should still call stop() after you are done so the socket can be closed.
    def start(self):
        self.threaded = True
        if self.streaming_enabled:
            self.thread.start()
        return self
    
    

    def stop(self):
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join()
        self.server_socket.close()
        print("Streamer resources released.")