from math import sin, cos, tan, pi
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# L1 = wheelbase of car
# L2 = 'wheelbase' of trailer
# M1 = trailer hitch offset
L1 = 5  # inches
L2 = 7  # inches
M1 = 1  # inches


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


def main():
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
        5,
        5,
        10,
        10,
        5,
        5,
        -5,
        -5,
        -10,
        -10,
        -5,
        -5,
        -5,
        -5,
        -8,
        -8,
        -10,
        -10,
    ]  # degrees
    # construct input array
    u1 = np.array(v1)
    u2 = np.array(str) * pi / 180  # radians
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
    x2 = yout[
        0,
    ]
    y2 = yout[
        1,
    ]
    theta2 = yout[
        2,
    ]
    beta2 = yout[
        3,
    ]

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
    main()
