from math import sin, cos, tan, pi
import sys
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# TODO: Make better documentation after discussing with Dr. Schwarz

# L1 = wheelbase of car
# L2 = 'wheelbase' of trailer
# M1 = trailer hitch offset
L1 = 5  # inches # curr: 6
L2 = 7  # inches # curr: 11.75
M1 = 1  # inches # curr: 2


def trailer1_step(tspan, y0, u, p, N=10):
    """
    The size of one step is defined by tspan. It could be
    any length, but you can only change the input between
    steps.
    """

    def dydt(t, y):
        """
        This is the system of ordinary differential equations
        that describes the car and trailer.
        """
        nonlocal u, p

        # p = [L1, M1, L2]
        L1 = p[0]
        M1 = p[1]
        L2 = p[2] 

        # why ???

        # u = [v1 steer]
        v1 = u[0]
        alpha = u[1]

        # y = (x2, y2, theta2, beta2)
        x2 = y[0]
        y2 = y[1]
        theta2 = y[2]
        beta2 = y[3]

        # inputs = v1, alpha
        # K = curvature
        K = tan(alpha) / L1

        # state update
        # beta2 = theta1 - theta2
        # x1dot = v1 * cos(theta1)
        # y1dot = v1 * sin(theta1)
        # theta1dot = v1 * K
        v2 = v1 * cos(beta2) + M1 * v1 * K * sin(beta2)
        x2dot = v2 * cos(theta2)
        y2dot = v2 * sin(theta2)
        theta2dot = v1 * (sin(beta2) / L2) - (M1 * v1 * K * cos(beta2) / L2)
        beta2dot = (v1 * K) - theta2dot

        dydt = [x2dot, y2dot, theta2dot, beta2dot]
        return dydt

    # solving ODE
    ts = np.linspace(tspan[0], tspan[1], N)
    sol = solve_ivp(dydt, tspan, y0, t_eval=ts)
    return [sol.t, sol.y]


def run_segment(t0, y0, u, tstep=1):
    p = [L1, M1, L2]
    tspan = [t0, t0 + tstep]
    [t, y] = trailer1_step(tspan, y0, u, p)
    return t, y


def compute_cost(y):
    """
    target state (for backing up):
        final x2: don't care
        final y2: 0
        final theta2: + if y2 is +, - if y2 is -, approach 0 as y2 approach 0
        final beta2: abs() < 30 degrees
    """
    y2 = y[1,]
    theta2 = y[2,]
    beta2 = y[3,]
    y2_final = y2[-1]
    theta2_final = theta2[-1] * 180 / pi
    theta2dot_final = (theta2[-1] - theta2[0]) * 180 / pi
    beta2_final = beta2[-1] * 180 / pi
    y2_target = 0
    theta2_target = y2[0]
    beta2_target = 0

    w = [0, 1, 0.5]

    cost = (
        w[0] * (y2_final - y2_target) ** 2
        + w[1] * (theta2_final - theta2_target) ** 2
        + w[2] * (beta2_final - beta2_target) ** 2
    )
    return cost


def func_eval(t0, y0, u, tstep=1):
    # estimate func derivative with small steering deviation
    eps = pi / 180  # 1 degree change in steering
    u_eps = [u[0], u[1] + eps]
    # evaluate the cost at a close point
    [t, y] = run_segment(t0, y0, u_eps, tstep)
    f_eps = compute_cost(y)
    # evaluate the cost at the original point
    [t, y] = run_segment(t0, y0, u, tstep)

    f = compute_cost(y)
    # compute the function change and estimate its derivative
    f_delta = f_eps - f
    f_deriv = f_delta / eps
    # suggest next steering input with newton's method
    str = u[1]
    str_next = (str - f / f_deriv) * 180 / pi
    str_next = -str_next  # negate to put back into steering reference frame
    return t, y, f, str_next


def plot_states(t, y):
    # unpack states
    # x = (x2, y2, theta2, beta2)
    x2 = y[0,]
    y2 = y[1,]
    theta2 = y[2,]
    beta2 = y[3,]
    theta2dot = np.diff(theta2)

    # derive car states
    theta1 = beta2 + theta2
    xhitch = x2 + L2 * np.cos(theta2)
    yhitch = y2 + L2 * np.sin(theta2)
    x1 = xhitch + M1 * np.cos(theta1)
    y1 = yhitch + M1 * np.sin(theta1)
    x0 = x1 + L1 * np.cos(theta1)
    y0 = y1 + L1 * np.sin(theta1)

    # path of car and trailer
    plt.plot(x1, y1, label="car")
    plt.plot(x2, y2, label="trailer")
    plt.xlabel("xpos (in)")
    plt.ylabel("ypos (in)")
    plt.legend()
    plt.show()
    plt.savefig('path.png')

    # angles of car and trailer
    plt.plot(t, theta1 * 180 / pi, label="theta1")
    plt.plot(t, theta2 * 180 / pi, label="theta2")
    plt.plot(t, beta2 * 180 / pi, label="beta2")
    plt.plot(t[1:], theta2dot * 180 / pi, label="theta2dot")
    plt.xlabel("time")
    plt.ylabel("ang (deg)")
    plt.legend()
    plt.show()
    plt.savefig('angles.png', dpi = 1000)


def grid_search(t0, y0, v1, tstep, str0):
    # coarse grid search
    str_vec = np.linspace(str0 - 20, str0 + 20, 21)
    # str_vec = np.linspace(-40, 40, 20)
    cost = []
    steer = []
    for str in str_vec:
        u = [v1, -str * pi / 180]
        [t, y, f, str_next] = func_eval(t0, y0, u, tstep)
        cost.append(f)
        steer.append(str)
        # print(f"str = {str:.2f}, cost = {f:.2f}, suggest str = {str_next:.2f}")
    imin = np.argmin(cost)
    str_min = int(steer[imin])

    # fine grid search
    str_vec_fine = np.linspace(str_min - 4, str_min + 4, 9)
    cost_fine = []
    steer_fine = []
    for str in str_vec_fine:
        # if np.sign(str) != sgn:
        #     continue
        u = [v1, -str * pi / 180]
        [t, y, f, str_next] = func_eval(t0, y0, u, tstep)
        cost_fine.append(f)
        steer_fine.append(str)
        # print(f"str = {str:.2f}, cost = {f:.2f}, suggest str = {str_next:.2f}")
    imin = np.argmin(cost_fine)
    str_min_fine = int(steer_fine[imin])

    # print("done searching. run once more with str_min")
    u = [v1, -str_min_fine * pi / 180]
    [t, y, f, str_next] = func_eval(t0, y0, u, tstep)
    # print(
    #     f"str = {str_min:.2f}, cost = {f:.2f}, direction ok is {direction_ok}, suggest str = {str_next:.2f}"
    # )
    return t, y, str_min_fine


def test_grid():
    # initial state
    t0 = 0
    # y0 = [0, 10, -10 * pi / 180, -5 * pi / 180]
    y0 = [0, -10, -10 * pi / 180, -5 * pi / 180]

    # time horizon
    tstep = 0.5
    # set constant speed input
    v1 = -6  # inches per second, negative for reverse

    # grid search
    tout = []
    yout = []
    time = []
    steer = []
    str0 = 20  # degrees
    for _ in range(100):
        [t, y, str_min] = grid_search(t0, y0, v1, tstep, str0)
        print(f"t0 = {t0}, str = {str_min}")
        # build up time and state
        if len(yout) == 0:
            tout = t
            yout = y
        else:
            tout = np.concatenate((tout, t), axis=0)
            yout = np.concatenate((yout, y), axis=1)
        time.append(t0)
        steer.append(str_min)
        # prepare for next loop
        tfinal = t[-1]
        yfinal = [y[0, -1], y[1, -1], y[2, -1], y[3, -1]]
        t0 = tfinal
        y0 = yfinal
        str0 = str_min

    # angles of car and trailer
    plt.plot(time, steer, label="steer")
    plt.xlabel("time")
    plt.ylabel("steer")
    plt.legend()
    plt.show()

    plot_states(tout, yout)


def test_newtons():
    # initial state
    t0 = 0
    # y0 = [0, 10, -10 * pi / 180, -5 * pi / 180]
    y0 = [0, -10, -10 * pi / 180, -5 * pi / 180]

    # time horizon
    tstep = 0.5
    # set constant speed input
    v1 = -6  # inches per second, negative for reverse

    str0 = 20
    u = [v1, -str0 * pi / 180]
    [t, y, f1, str_next1] = func_eval(t0, y0, u, tstep)
    print(f"str = {str0:.2f}, cost = {f1:.2f}, suggest str = {str_next1:.2f}")

    str0 = -20
    u = [v1, -str0 * pi / 180]
    [t, y, f2, str_next2] = func_eval(t0, y0, u, tstep)
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
        [t, y, f, str_next] = func_eval(t0, y0, u, tstep)
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
        y0 = yfinal

    # angles of car and trailer
    plt.plot(time, steer, label="steer")
    plt.xlabel("time")
    plt.ylabel("steer")
    plt.legend()
  
        #plt.show()
    plt.savefig('plot.png')

    plot_states(tout, yout)


def test1():
    """
    Define a vector of inputs and call a time step for each one.
    tstep is the size of one time step
    inputs u = [u1, u2] = [v1, str]
    If the lengths are given in inches, then I think the units
    of speed should be in/sec

    TODO: measure vehicle to calibrate lengths
    """
    tstep = 1  # seconds
    # u = [v1 steer]
    p = [L1, M1, L2]

    # set up n-length arrays for n steps of simulation
    # forward circles
    # v1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # str = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30]
    # forward backward complex
    v1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1]
    str = [
        0,
        0,
        -5,
        -5,
        -10,
        -10,
        -5,
        -5,
        5,
        5,
        10,
        10,
        5,
        5,
        5,
        5,
        8,
        8,
        10,
        10,
    ]  # degrees
    # construct input array
    u1 = np.array(v1)
    u2 = np.array(-str) * pi / 180  # radians
    n = len(u1)
    tin = np.linspace(0, tstep * n, num=n + 1)
    y0 = [0, 0, 0, 0]
    tout = []
    yout = []

    for i in range(len(u1)):
        print(f"i = {i}, len(u1) = {len(u1)}")
        u = [u1[i], u2[i]]
        tspan = [tin[i], tin[i + 1]]
        [t, y] = trailer1_step(tspan, y0, u, p)
        y0 = [y[0, -1], y[1, -1], y[2, -1], y[3, -1]]

        if len(yout) == 0:
            tout = t
            yout = y
        else:
            tout = np.concatenate((tout, t), axis=0)
            yout = np.concatenate((yout, y), axis=1)

    # unpack states
    # x = (x2, y2, theta2, beta2)
    x2 = yout[0,]
    y2 = yout[1,]
    theta2 = yout[2,]
    beta2 = yout[3,]

    # derive car states
    theta1 = beta2 + theta2
    xhitch = x2 + L2 * np.cos(theta2)
    yhitch = y2 + L2 * np.sin(theta2)
    x1 = xhitch + M1 * np.cos(theta1)
    y1 = yhitch + M1 * np.sin(theta1)
    x0 = x1 + L1 * np.cos(theta1)
    y0 = y1 + L1 * np.sin(theta1)

    # path of car and trailer
    plt.plot(x1, y1, label="car")
    plt.plot(x2, y2, label="trailer")
    plt.xlabel("xpos")
    plt.ylabel("ypos")
    plt.legend()
    plt.show()

    # angles of car and trailer
    plt.plot(tout, theta1, label="theta1")
    plt.plot(tout, theta2, label="theta2")
    plt.plot(tout, beta2, label="beta2")
    plt.xlabel("xpos")
    plt.ylabel("ypos")
    plt.legend()
    plt.show()

    # car-trailer animation
    fig, ax = plt.subplots()
    ax.set_xlim(min(np.min(x2), np.min(x0)), max(np.max(x2), np.max(x0)))
    ax.set_ylim(min(np.min(y2), np.min(y0)), max(np.max(y2), np.max(y0)))
    (line,) = ax.plot([x2[0], xhitch[0], x0[0]], [y2[0], yhitch[0], y0[0]])

    def animate(i):
        line.set_xdata([x2[i], xhitch[i], x0[i]])
        line.set_ydata([y2[i], yhitch[i], y0[i]])
        return (line,)

    ani = animation.FuncAnimation(fig, animate, interval=1, blit=True, save_count=5)

    plt.show()


if __name__ == "__main__":
    # test_newtons()
    test_grid()