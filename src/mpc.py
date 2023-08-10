from state_informer import StateInformer
from model_predictive_control.trailer1 import func_eval
import numpy as np
from math import pi

class Predicter:
    def __init__(self, state_informer: StateInformer):
        self.state_informer = state_informer
        self.trailer_deviation = state_informer.get_trailer_deviation()
        self.trailer_lane_angle = state_informer.get_trailer_lane_angle()
        self.hitch_angle = state_informer.get_hitch_angle()
        self.x = 0
        self.state_vector = [self.x, self.trailer_deviation, self.trailer_lane_angle * pi / 180, self.hitch_angle * pi / 180]

    def predict(self):

        str0 = self.state_informer.get_steering_angle()
        v1 = 2
        t0 = 0 # need to change to live time probably
        tstep = .5
        x = 0 # don't care about distance traveled
      

        state_vector = self.state_vector

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
        #print(str_min_fine)
        if self.state_informer.get_vel() ==  0:
            return 0, cost
        #print(state_informer.get_vel())
        
        return -str_min_fine, cost
    
    def predict_fast(self, str, v1, t0, y0, tstep):
        
        steps = 0
        f_prev = 9999
        delta_str = 9999
        # Newton's method
        # print("newton")

        while True:
            u = [v1, str * pi / 180]
            [t, y, f, str_next] = func_eval(t0, y0, u, tstep)
            steps = steps + 1
            str_next = str_next * 180 / pi
            if abs(str_next - str) > 2.0 * delta_str:
                sgn = np.sign(str_next - str)
                str_next = str + sgn * min(2.0, 2.0 * delta_str)
            else:
                if steps > 1:
                    delta_str = abs(str_next - str)
            if f > f_prev:
                break
            str_prev = str
            str = str_next
            f_prev = f

        # the cost function may not intersect 0 which screws with Newton
        # use bisection to narrow in on the minimum
        # ignore new str_next return values for this part
        # print("bisection")
        strv = [str_prev, str]
        fv = [f_prev, f]
        while True:
            if abs(strv[1] - strv[0]) < 0.5:
                break
            str = 0.5 * (strv[0] + strv[1])
            strv.append(str)
            u = [v1, str * pi / 180]
            [t, y, f, str_next] = func_eval(t0, y0, u, tstep)
            steps = steps + 1
            fv.append(f)
            i = np.argmax(fv)
            if i == 2:
                break
            strv.pop(i)
            fv.pop(i)

        i = np.argmin(fv)
        str_next = strv[i]

        return t, y, f, str_next, steps