    # print('1', steering_angle)
    # stable_angle = car.stabilize_steering_angle(steering_angle, num_lanes)
    # print('2', stable_angle)
car.set_steering_angle(stable_angle)
    def stabilize_steering_angle(
        self, 
        new_angle, 
        num_of_lane_lines, 
        max_angle_deviation_two_lines=40, 
        max_angle_deviation_one_line=40, 
    ):
        if num_of_lane_lines == 2:
            max_angle_deviation = max_angle_deviation_two_lines
        else:
            max_angle_deviation = max_angle_deviation_one_line

        angle_deviation = new_angle - self.current_steering_angle
        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = int(
                self.current_steering_angle + 
                max_angle_deviation * angle_deviation / abs(angle_deviation)
            )
        else:
            stabilized_steering_angle = new_angle

        self.current_steering_angle = stabilized_steering_angle
        return stabilized_steering_angle
