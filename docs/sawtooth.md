# Approximating a sawtooth wave via additive synthesis

Additive synthesis is the process of approximating complex waveforms
by adding sine waves together.  In this example, we look at how
additive synthesis can be used to approximate a *reverse* sawtooth
waveform.

We're looking at the reverse version because this makes the additive
process more obvious (the non-reversed version involves inverting the
waveform, which just makes it a little harder to line things up
visually).

## Waveform equation

A reverse sawtooth waveform can be represented by the following
equation:

$$
x_\mathrm{reversesawtooth}(t) = \frac {2}{\pi}\sum_{k=1}^{\infty}
{(-1)}^{k} \frac {\sin (2\pi kft)}{k}
$$

Where $f$ is the frequency of the desired waveform, $k$ is the
*order*, or number of harmonics to use for the approximation, and $t$
is the duration of the waveform.

## Waveform code

Using [NumPy][] we can perform a relatively straightforward
translation of the above equation into the following Python code:

[numpy]: http://www.numpy.org/

~~~ {.python}
import numpy as np

order = 30
t = np.linspace(0, np.pi, 500)
waveform = (2/np.pi) * sum([
    (-1**k) * np.sin(2 * np.pi * k * t)/k
    for k in range(1, (order+1))
])
~~~

Which results in:

<img src="example1.svg" width="400" />

## Approximation in detail

The following figure shows the result of each successive step as $k$
iterates from 1 to 10.

![Successive approximation of a sawtooth waveform](sawtooth-steps.svg)
