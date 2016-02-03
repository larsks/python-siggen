from __future__ import division

from numpy import linspace, sin, pi
import matplotlib.pyplot as plt

mainfig = plt.figure(figsize=(8, 10))
t = linspace(0, pi, 500)

for p, order in enumerate(range(0, 10)):
    d = [
        (-1)**k *
        sin(2 * pi * (2 * k + 1) * t) /
        (2 * k + 1)**2
        for k in range(0, (order+1))
    ]

    ax = mainfig.add_subplot(10, 2, (2 * p)+1)
    ax.set_ylabel('order=%d' % (order+1))
    ax.yaxis.set_ticks([-2, -1, 0, 1, 2])
    ax.xaxis.set_ticks([])
    ax.set_autoscaley_on(False)
    ax.set_ylim([-1.5, 1.5])
    ax.plot(d[-1])

    d = (8/(pi**2)) * sum(d)
    ax = mainfig.add_subplot(10, 2, (2*p)+2)
    ax.yaxis.set_ticks([-2, -1, 0, 1, 2])
    ax.xaxis.set_ticks([])
    ax.set_autoscaley_on(False)
    ax.set_ylim([-1.5, 1.5])
    ax.plot(d)

mainfig.tight_layout()
mainfig.savefig('triangle-steps.svg')
