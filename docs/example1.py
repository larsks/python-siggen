import numpy as np
import matplotlib.pyplot as plt

order = 30
t = np.linspace(0, np.pi, 500)
waveform = (2/np.pi) * sum([
    (-1**k) * np.sin(2 * np.pi * k * t)/k
    for k in range(1, (order+1))
])

plt.plot(waveform)
plt.savefig('example1.svg')
