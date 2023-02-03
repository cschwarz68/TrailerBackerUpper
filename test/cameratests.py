import io
import time
import picamera
import timeit


def main():
    with picamera.PiCamera() as camera:
        stream = io.BytesIO()
        i = 0
        for foo in camera.capture_continuous(
            stream, format="jpeg", use_video_port=True
        ):
            # Truncate the stream to the current position (in case
            # prior iterations output a longer image)
            stream.truncate()
            stream.seek(0)
            if i >= 10:
                break
            i = i + 1


def image_time():
    SETUP_CODE = """
from __main__ import main
"""

    TEST_CODE = """
main()"""

    # timeit.repeat statement
    times = timeit.timeit(setup=SETUP_CODE, stmt=TEST_CODE, number=1)

    # printing minimum exec. time
    print("Image test time: {}".format(times))


if __name__ == "__main__":
    image_time()
