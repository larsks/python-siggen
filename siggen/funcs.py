from __future__ import division

import numpy as np
import scipy.signal as signal


def sin(freq, rate=44100):
    period = rate/freq
    factor = freq * 2 * np.pi / rate
    return np.sin(np.arange(period) * factor).astype(np.float32)


def square(freq, rate=44100):
    period = rate/freq
    factor = freq * 2 * np.pi / rate
    return signal.square(np.arange(period) * factor).astype(np.float32)


def triangle(freq, rate=44100):
    period = rate/freq
    factor = freq * 2 * np.pi / rate
    return signal.sawtooth(np.arange(period) * factor,
                           width=0.5).astype(np.float32)


def sawtooth(freq, rate=44100):
    period = rate/freq
    factor = freq * 2 * np.pi / rate
    return signal.sawtooth(np.arange(period) * factor).astype(np.float32)
