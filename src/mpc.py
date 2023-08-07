from state_informer import StateInformer
from model_predictive_control.trailer1 import func_eval
import numpy as np
from math import pi

class Predicter:
    def __init__(self):
        pass

    def predict(self, state_informer: StateInformer):

        str0 = state_informer.get_steering_angle()
        v1 = 2
        t0 = 0 # need to change to live time probably
        tstep = .5
        x = 0 # don't care about distance traveled
        trailer_deviation = state_informer.get_trailer_deviation()
        trailer_lane_angle = state_informer.get_trailer_lane_angle()
        hitch_angle = state_informer.get_hitch_angle()

        state_vector = [x, trailer_deviation, trailer_lane_angle * pi / 180, hitch_angle * pi / 180]

        str_vec = np.linspace(str0 - 5, str0 + 5, 5)
        cost = []
        steer = []
        
        for str in str_vec:
            u = [v1, -str * pi / 180]
            [t, trailer_deviation, f, str_next] = func_eval(t0, state_vector, u, tstep)
            
            cost.append(f)
            steer.append(str)

        imin =  np.argmin(cost)
        str_min = int(steer[imin])

        # fine grid search

        str_vec_fine = np.linspace(str_min - 4, str_min + 4, 9)
        cost_fine = []
        steer_fine = []

        for str in str_vec_fine:

            u = [v1, -str * pi / 180]
            [t, trailer_deviation , f, str_next] = func_eval(t0, state_vector, u, tstep)
            cost_fine.append(f)
            steer_fine.append(str)

        imin = np.argmin(cost_fine)
        str_min_fine = int(steer_fine[imin])

        u = [v1, -str_min_fine * pi / 180]
        [t, trailer_deviation, f, str_next] = func_eval(t0, state_vector, u, tstep)

        #return t, trailer_deviation , str_min_fine
        print(str_min_fine)
        if state_informer.get_vel() ==  0:
            return 0, cost
        #print(state_informer.get_vel())
        
        return -str_min_fine, cost
    
    def predict_fast(self, state_informer: StateInformer):
        # initial state
        t0 = 0
        # y0 = [0, 10, -10 * pi / 180, -5 * pi / 180]
        x = 0 
        trailer_deviation = state_informer.get_trailer_deviation()
        trailer_lane_angle = state_informer.get_trailer_lane_angle()
        hitch_angle = state_informer.get_hitch_angle()
        state_vector = [x, trailer_deviation, trailer_lane_angle, hitch_angle]

        # time horizon
        tstep = 0.5
        # set constant speed input
        v1 = -6  # inches per second, negative for reverse

        str0 = 20
        u = [v1, -str0 * pi / 180]
        [t, y, f1, str_next1] = func_eval(t0, state_vector, u, tstep)
        print(f"str = {str0:.2f}, cost = {f1:.2f}, suggest str = {str_next1:.2f}")

        str0 = -20
        u = [v1, -str0 * pi / 180]
        [t, y, f2, str_next2] = func_eval(t0, state_vector, u, tstep)
        print(f"str = {str0:.2f}, cost = {f2:.2f}, suggest str = {str_next2:.2f}")

        if f1 < f2:
            str_next = str_next1
        else:
            str_next = str_next2

        # Newton's method
        tout = []
        yout = []
        time = []
        steer = []
        for i in range(5):
            str = str_next
            u = [v1, -str * pi / 180]
            [t, y, f, str_next] = func_eval(t0, state_vector, u, tstep)
            print(f"str = {str:.2f}, cost = {f:.2f}, suggest str = {str_next:.2f}")
            # build up time and state
            if len(yout) == 0:
                tout = t
                yout = y
            else:
                tout = np.concatenate((tout, t), axis=0)
                yout = np.concatenate((yout, y), axis=1)
            time.append(t0)
            steer.append(str)
            # prepare for next loop
            tfinal = t[-1]
            yfinal = [y[0, -1], y[1, -1], y[2, -1], y[3, -1]]
            t0 = tfinal
            state_vector = yfinal