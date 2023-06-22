# def preview_test():
#     with picamera.PiCamera() as camera:
#         camera.start_preview(alpha=5)
#         camera.resolution = (640, 480)
#         time.sleep(2)
#         with picamera.array.PiRGBArray(camera) as stream:
#             camera.capture(stream, format="bgr")
#             image = stream.array
#             cv2.imshow("img", image)
#             cv2.waitKey()