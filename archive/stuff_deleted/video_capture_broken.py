# def video_capture():
#     global stream, steer
#     # Processing and capture test.
#     image = stream.capture()
#     edges = ip.edge_detector(image)
#     cropped_edges = ip.region_of_interest(edges)
#     line_segments = ip.detect_line_segments(cropped_edges)
#     lane_lines = ip.average_slope_intercept(image, line_segments)
#     # num_lanes = len(lane_lines)
#     line_image = ip.display_lines(image, lane_lines)
#     # Recording.
#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#     out = cv2.VideoWriter(
#         "test_recording.mp4", fourcc, 20.0, (320, 240)
#     )
#     while True:
#         frame = cv2.cvtColor(
#             np.array(line_image), cv2.COLOR_GRAY2BGR
#         )
#         out.write(frame)
#         steering_angle = ip.compute_steering_angle(
#             line_image, lane_lines
#         )
#         steer.steer_by_angle(steering_angle)

#     elif pressed["Key"]["BTN_SOUTH"] == 1:
#         pass # Bypassing functionality for now.
#         # video_capture()
