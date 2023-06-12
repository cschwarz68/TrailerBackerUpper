from inputs import get_gamepad

class Gamepad:
    
    def __init__(self):
        self.events = get_gamepad()
        self.pressed = self.get_pressed(self.events, [
            ("Key", "BTN_EAST"), 
            ("Key", "BTN_SOUTH"), 
            ("Key", "BTN_WEST"), 
            ("Key", "BTN_NORTH"), 
            ("Key", "BTN_START"), 
            ("Key","BTN_SELECT")
            ("Absolute", "ABS_RX"),
            ("Absolute","ABS_RY") 
            ("Absolute", "ABS_Y"),
            ("Absolute", "ABS_X")
        ])

    def get_pressed(self, events, require : list[tuple[str, str]]) -> dict[str, dict[str, int]]:
        ret = dict()
        for key in require:
            if key[0] not in ret:
                ret[key[0]] = dict()
            ret[key[0]][key[1]] = None
        for event in events:
            # print(event.ev_type, event.code, event.state) # For debugging.
            if event.ev_type in ret and event.code in ret[event.ev_type]:
                ret[event.ev_type][event.code] = event.state
        return ret

    def a_pressed(self, pressed : dict[str, dict[str, int]]) -> bool:
        return pressed["Key"]["BTN_SOUTH"] == 1

    def b_pressed(self, pressed : dict[str, dict[str, int]]) -> bool:
        return pressed["Key"]["BTN_EAST"] == 1

    def x_pressed(self, pressed : dict[str, dict[str, int]]) -> bool:
        return pressed["Key"]["BTN_NORTH"] == 1
    
    def y_pressed(self, pressed : dict[str, dict[str, int]]) -> bool:
        return pressed["Key"]["BTN_WEST"] == 1

    def start_pressed(self, pressed : dict[str, dict[str, int]]) -> bool:
        return pressed["Key"]["BTN_SOUTH"] == 1
    
    def a_pressed(self, pressed : dict[str, dict[str, int]]) -> bool:
        return pressed["Key"]["BTN_SOUTH"] == 1


def main():
    """Just print out some event infomation when the gamepad is used."""
    while 1:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)

if __name__ == "__main__":
    main()





def manual(events):
    global done, steer, drive, mode, transition_mode
    """
    This commented code uses the is_pressed function.
    Use in case get_pressed is buggy.
    """
    # if is_pressed(events, "Key", "BTN_EAST", 1)[0]:
        # done = True
    # elif is_pressed(events, "Key", "BTN_SOUTH", 1)[0]:
        # pass # Bypassing functionality for now.
        # video_capture()
    # event_x = is_pressed(events, "Absolute", "ABS_RX", None)[1] # RX refers to the right joystick.
    # event_y = is_pressed(events, "Absolute", "ABS_Y", None)[1]
    # if event_x is not None:
    #     x = float(event_x.state) / Drive_Params.TURN_MAX
    #     steer.steer(x)
    # if event_y is not None:
    #     y = float(event_y.state) / Drive_Params.TURN_MAX
    #     drive.drive(-y)
    """
    IMPORTANT

    On the controller:

            Y                  West
          X + B    -->    North + East
            A                 South
    """
    # pressed = get_pressed(events, [
    #     ("Key", "BTN_EAST"), 
    #     ("Key", "BTN_SOUTH"), 
    #     ("Key", "BTN_WEST"), 
    #     ("Key", "BTN_NORTH"), 
    #     ("Key", "BTN_START"), 
    #     ("Absolute", "ABS_RX"), 
    #     ("Absolute", "ABS_Y")
    # ])
    # if pressed["Key"]["BTN_EAST"] == 1:
    #     done = True
    # elif pressed["Key"]["BTN_SOUTH"] == 1:
    #     pass # Bypassing functionality for now.
    #     # video_capture()
    # elif pressed["Key"]["BTN_NORTH"] == 1:
    #     transition_mode = Main_Mode.AUTO_FORWARD
    #     print("Transitioned to auto FORWARD. Press START to init.")
    # elif pressed["Key"]["BTN_WEST"] == 1:
    #     transition_mode = Main_Mode.AUTO_REVERSE
    #     print("Transitioned to auto REVERESE. Press START to init.")
    # elif pressed["Key"]["BTN_START"] == 1:
    #     print("Entered Mode:", transition_mode)
    #     mode = transition_mode
    # x = pressed["Absolute"]["ABS_RX"]
    # y = pressed["Absolute"]["ABS_Y"]
    # if x is not None:
    #     steer.steer(x / Drive_Params.JOYSTICK_MAX)
    # if y is not None:
    #     drive.drive(-y / Drive_Params.JOYSTICK_MAX)
