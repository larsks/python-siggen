# Python Signal Generator

This is a simple audio signal generator designed for a STEM night
demonstration at our local elementary school.  It is designed to send
audio output to an oscilloscope, to demonstrate the different sounds
that correspond to different audio waveforms.  It is designed to be
controlled by a Korg [nanoKONTROL2][], although any MIDI controller
with a sufficient number of sliders and knobs should work.

[nanokontrol2]: http://www.korg.com/us/products/controllers/nanokontrol2/

This project uses [PYO][], a fantastic Python audio processing module.
My code barely scratches the surface of what you can do with it.

[pyo]: http://ajaxsoundstudio.com/software/pyo/

## Configuration

Siggen reads configuration from a [YAML][] format configuration file,
by default named `signals.yml`.  The file has three main sections:

[YAML]: http://www.yaml.org/

- `devices`
- `controls`
- `mixers`

See below for details.  An example configuration file is included in
the distribution.

### Devices

The `devices` section identifies the audio and MIDI devices that will
be used by siggen:

    devices:
      midi:
        name: nanoKONTROL2 MIDI 1
      input:
        name: Scarlett 2i2 USB
        channels: 1

Devices may be identified by name, in which case siggen will use the
first device whose prefix matches the given name.  For example, I
could have specified my MIDI controller as simply `nano`.  Devices may
also be identified using the portaudio or portmidi integer index; to
see a list of available devices and indexes, you can run:

    $ siggen -l

### Controls

The `controls` section maps MIDI controls to synthesizer attributes
(like volume and frequency) and global actions (like `play` and
`stop`). The various signal generators all have `freq` and `volume`
keys, while other controls may not.  My configuration looks like this:

    # Map MIDI control change messages to actions
    controls:
      sine:
        freq: 16
        volume: 102

      square:
        freq: 17
        volume: 103

      triangle:
        freq: 18
        volume: 104

      sawtooth:
        freq: 19
        volume: 105

      passthrough:
        volume: 107

      play: 41
      stop: 42

### Mixers

The `mixers` section links MIDI controls to ALSA devices.  For
example, on my Raspberry Pi with a USB sound module, running `asmixer`
returns:

    Simple mixer control 'Speaker',0
      Capabilities: pvolume pswitch pswitch-joined
      Playback channels: Front Left - Front Right
      Limits: Playback 0 - 37
      Mono:
      Front Left: Playback 23 [62%] [-14.00dB] [on]
      Front Right: Playback 23 [62%] [-14.00dB] [on]
    Simple mixer control 'Mic',0
      Capabilities: pvolume pvolume-joined cvolume cvolume-joined pswitch pswitch-joined cswitch cswitch-joined
      Playback channels: Mono
      Capture channels: Mono
      Limits: Playback 0 - 31 Capture 0 - 35
      Mono: Playback 19 [61%] [-4.00dB] [off] Capture 22 [63%] [10.00dB] [on]
    Simple mixer control 'Auto Gain Control',0
      Capabilities: pswitch pswitch-joined
      Playback channels: Mono
      Mono: Playback [on]

I created the following `mixers` section to interact with these
devices:

    mixers:
      default:
        Speaker:
          output:
            FRONT_LEFT: 108
            FRONT_RIGHT: 109
        Mic:
          output:
            MONO: 107
          capture:
            MONO: 21

This attaches MIDI control 108 and 109 to the left and right channels
of the main output, and then connects control 107 to the Microphone
volume and control 21 to the Capture volume.

## Notes for developers

Just some miscellaneous notes about my experiences writing this
software.

### PYO

While PYO is very flexible and has well designed abstractions, it can
be a little fragile.  In particular, it doesn't seem to do a very good
job of introspecting the capabilities of audio devices, such that you
will often see something like this:

    >>> from pyo import *
    >>> s = Server().boot()
    [...]
    Expression 'parameters->channelCount <= maxChans' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 1513
    Expression 'ValidateParameters( inputParameters, hostApi, StreamDirection_In )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 2813
    portaudio error in Pa_OpenStream: Invalid number of channels
    Portaudio error: Invalid number of channels
    Server not booted.

This simply means that you are trying to use a device that doesn't
support the default number of channels (2).  A common cause of this
behavior is a mono microphone, which only has a single channel, in
which case you want:

    >>> from pyo import *
    >>> s = Server(ichnls=1).boot()

If you want to specify explicit input or output devices, you must do
this *before* calling the `boot()` method.  For example:

    >>> from pyo import *
    >>> s = Server()
    >>> s.setInputDevice(11)
    >>> s.boot()
