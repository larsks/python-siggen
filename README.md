# Python Signal Generator

This is a simple audio signal generator designed for a STEM night
demonstration at our local elementary school.  My goal was to have
some buttons and knobs that kids could fiddle with to make weird
sounds, and to display the resulting waveforms on an oscilloscope.

The knobs and button were provided by a Korg [nanoKONTROL2][],
although any MIDI controller will work. The sounds were provided by
this project.

[nanokontrol2]: http://www.korg.com/us/products/controllers/nanokontrol2/

## Thanks

This project uses [PYO][], a fantastic Python audio processing module.
My code barely scratches the surface of what you can do with it.

[pyo]: http://ajaxsoundstudio.com/software/pyo/

## Configuration

Siggen reads configuration from a [YAML][] format configuration file,
by default named `siggen.yml`.  The file has the following major
configuration sections:

[YAML]: http://www.yaml.org/

- `devices`

  This section identifies the sound and MIDI devices used by siggen.

- `controls`

  This section maps MIDI controls to global actions (such as "stop all
  synths" or "start all synths").

- `synths`

  This section declares the synthesizers that will be instantiated by
  siggen, and maps MIDI controls to synthesizer attributes such as
  frequency and volume.

- `mixers`

  This section maps MIDI controls to ALSA audio devices.

- `external`

  This section maps MIDI controls to shell scripts.

- `tables`

  This section sets values used by some of the wavetable generation
  routines.

An example configuration file is included in the distribution.

### Devices

The `devices` section identifies the audio and MIDI devices that will
be used by siggen.  For example:

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

The `controls` section maps MIDI controls to global actions.  For
example:

    controls:
      play: 41
      stop: 42

### Synths

The `synths` section declares synthesizer.  It is a YAML list of
dictionaries, each of which must have a `type` key identifying the
synthesizer type.  For example, the following would create a sine wave
synth and a square wave synth:

    synths:
      - type: sine
        freq: 16
        volume: 102

      - type: square
        freq: 17
        volume: 103

Each synth may also specify a `freq` control that will control the
synthesizer frequency and a `volume` control that will control the
synthesizer volume.

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
          capture:
            MONO: 20

This attaches MIDI control 108 and 109 to the left and right channels
of the main output, and then connects control 20 to the Mic capture
volume.

### Tables

The `tables` section specifies values that are used by to create wave
tables.

- `nharmonics` -- the number of harmonics to use to approximate a
  signal (defaults to 30).

- `tsize` -- The wave table size.  Defaults to the PYO default of
  8192, but PYO seems to have problems with this on some systems.

For example:

    tables:
      tsize: 1024

### External

The `external` section maps MIDI controls to external scripts.  For
example:

    external:
      - control: 41
        script: |
          #!/bin/sh
          echo hello world

**WARNING** Running external scripts seems to break PYO, so unless
your script causes siggen to exit (see the `rpi-config` directory for
an example), you should probably be careful around this.

## Synth types

Siggen supports several synthesizer types.

### Sine

- `sine` -- your basic sine wave

### Additive synthesis

These are generated with the PYO [HarmTable][] class.

- `square`
- `triangle`
- `sawtooth`

### Linear

These are generated with the PYO [LinTable][] class.

- `square_line`
- `triangle_line`
- `sawtooth_line`

### Other

- `passthrough`

  This isn't really a synth; it passes input from a microphone (etc)
  to your output.  I use this for displaying voices on an attached
  oscilloscope.

[lintable]: http://ajaxsoundstudio.com/pyodoc/api/classes/tables.html#lintable
[harmtable]: http://ajaxsoundstudio.com/pyodoc/api/classes/tables.html#harmtable

## PYO: Notes for developers

The interaction between PYO and portaudio seems a little fragile.  I
think this may be more of a problem with portaudio, based on where the
crashes were happening.

I ended up switching to [jack][] on my Raspberry Pi, and most of the
problems I was having with crashing and event loop lockups
disappeared.

[jack]: http://www.jackaudio.org/

