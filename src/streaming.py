"""
From ancabilloni/udp_camera_streaming. https://github.com/ancabilloni/udp_camera_streaming
"""

from struct import pack
import cv2
import math

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
            try:
                self.s.sendto(pack("B", count) + dat[array_pos_start:array_pos_end], (self.addr, self.port))
            except OSError:
                print("Streaming Error: Exception caught when trying to send data; dropping packet.")
            array_pos_start = array_pos_end
            count -= 1
