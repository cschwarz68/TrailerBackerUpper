"""
Source code for car camera feed streaming client.

Does not work on DSRI facility desktops. Bring your own computer.
"""

from cv2 import imdecode, imshow, waitKey, destroyAllWindows
from socket import socket, AF_INET, SOCK_DGRAM
from numpy import fromstring, uint8
from struct import unpack

# Change this value if you would like to use a different port (default is 25565).
PORT = 25565
# NOTE: You cannot run this program and play multiplayer Minecraft at the same time if you are using port 25565.


MAX_DGRAM = 2 ** 16

def dump_buffer(s: socket):
    # Emptying buffer frame.
    while True:
        seg, _ = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if unpack("B", seg[0:1])[0] == 1:
            print("Finish emptying buffer.")
            break

def main():
    # Get image UDP frame & concatenate before decoding and outputting the image.
    # Set up socket.
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('0.0.0.0', PORT)) # Minecraft port (picked arbitrarily).
    dat = b''
    dump_buffer(s)

    while True:
        seg, _ = s.recvfrom(MAX_DGRAM)
        if unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = imdecode(fromstring(dat, dtype=uint8), 1)
            imshow("Camera Feed", img)
            if waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    destroyAllWindows()
    s.close()

if __name__ == "__main__":
    main()
