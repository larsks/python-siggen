from __future__ import division

import numpy as np
import matplotlib.pyplot as plt

mainfig = plt.figure(figsize=(8, 10))
t = np.linspace(0, np.pi, 500)

for p, order in enumerate(range(0, 10)):

    d = [
        np.sin(2 * np.pi * (2 * k - 1) * t)/(2 * k - 1)
        for k in range(1, (order+2))
    ]

    ax = mainfig.add_subplot(10, 2, (2 * p)+1)
    ax.set_ylabel('order=%d' % (order+1))
    ax.yaxis.set_ticks([-2, -1, 0, 1, 2])
    ax.xaxis.set_ticks([])
    ax.set_autoscaley_on(False)
    ax.set_ylim([-1.5, 1.5])
    ax.plot(d[-1])

    d = (4/np.pi) * sum(d)
    ax = mainfig.add_subplot(10, 2, (2*p)+2)
    ax.yaxis.set_ticks([-2, -1, 0, 1, 2])
    ax.xaxis.set_ticks([])
    ax.set_autoscaley_on(False)
    ax.set_ylim([-1.5, 1.5])
    ax.plot(d)

mainfig.tight_layout()
mainfig.savefig('square-steps.svg')
