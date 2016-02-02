# Approximating waveforms via additive synthesis

Additive synthesis is the process of approximating waveforms by adding
sine waves together.  In this article, we look at how additive
synthesis can be used to approximate basic waveforms.

## Sawtooth

### Equation

A reverse sawtooth waveform can be represented by the following
equation:

$$
x_\mathrm{reversesawtooth}(t) = \frac {2}{\pi}\sum_{k=1}^{\infty}
{(-1)}^{k} \frac {\sin (2\pi kft)}{k}
$$

Where $f$ is the frequency of the desired waveform, $k$ is the
*order*, or number of harmonics to use for the approximation, and $t$
is the duration of the waveform.

### Code

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

### Steps

The following figure shows the result of each successive step as $k$
iterates from 1 to 10.

![Successive approximation of a sawtooth waveform](sawtooth-steps.svg)

## Square

### Equation

$$
x_{\mathrm{square}}(t) = \frac{4}{\pi} \sum_{k=1}^\infty
{\sin{\left (2\pi (2k-1) ft \right )}\over(2k-1)}
$$

### Code

~~~ {.python}
import numpy as np

order = 30
t = np.linspace(0, np.pi, 500)

waveform = (4/np.pi) * sum([
  np.sin(2 * np.pi * (2 * k - 1) * t)/(2 * k - 1)
  for k in range(1, (order+2))
])
~~~

<img src="example2.svg" width="400" />

### Steps

![Successive approximation of a square waveform](square-steps.svg)

