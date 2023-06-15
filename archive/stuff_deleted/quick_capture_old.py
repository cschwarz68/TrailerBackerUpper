
    # Tests if the camera is working by taking an image and saving it to disk.
    def test(self):
        self.camera.capture("quick_capture_module_test_image.png", format="bgr", use_video_port=True)
        self.camera.stop()

    # Captures and returns an array in BGR format.
    def stream_capture(self):
        with picamera2.array.PiRGBArray(self.camera) as stream:
            self.camera.capture(stream, format="bgr", use_video_port=True)
            image = stream.array
            image = cv2.flip(image,-1)
        return image
