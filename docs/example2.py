import numpy as np
import matplotlib.pyplot as plt

order = 30
t = np.linspace(0, np.pi, 500)
waveform = (4/np.pi) * sum([
    np.sin(2 * np.pi * (2 * k - 1) * t)/(2 * k - 1)
    for k in range(1, (order+2))
])

plt.plot(waveform)
plt.savefig('example2.svg')
