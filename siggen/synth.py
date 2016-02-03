from __future__ import division

from six import string_types
from functools import partial
from pyalsa import alsamixer
from itertools import cycle
import logging
import pyo

from .exc import *  # NOQA

FREQ_A0 = 27.5
FREQ_C8 = 4186
FREQ_C4 = 261.626
DEFAULT_NHARMONICS = 30
DEFAULT_TSIZE = 8192
LOG = logging.getLogger(__name__)


def calc_key_freq(value):
    key = int((value/127.0) * 88)
    freq = 2 ** ((key-49)/12) * 440
    LOG.debug('freq control value %d -> key %d -> freq %f',
              value, key, freq)
    return freq


def discover_pa_devices():
    return pyo.pa_get_devices_infos()


def discover_pm_devices():
    inputs = pyo.pm_get_input_devices()
    return dict(zip(inputs[1], inputs[0]))


class Synth(object):
    def __init__(self,
                 audio=None,
                 midiDevice=None,
                 outputDevice=None,
                 outputDeviceChannels=None,
                 inputDevice=None,
                 inputDeviceChannels=None,
                 synths=None,
                 mixers=None,
                 controls=None,
                 nharmonics=None,
                 tsize=None):

        self.init_log()

        self.synths = synths
        self.mixers = mixers
        self.controls = controls

        self.audio = audio
        self.inputDevice = inputDevice
        self.outputDevice = outputDevice
        self.midiDevice = midiDevice

        self.nharmonics = (
            nharmonics if nharmonics is not None
            else DEFAULT_NHARMONICS)
        self.tsize = (
            tsize if tsize is not None
            else DEFAULT_TSIZE)

        self.log.debug('table params: tsize = %d, nharmonics = %d',
                       self.tsize, self.nharmonics)

        self.discover_devices()

        kwargs = {}
        if audio is not None:
            kwargs['audio'] = audio
        if outputDeviceChannels is not None:
            kwargs['nchnls'] = outputDeviceChannels
        if inputDeviceChannels is not None:
            kwargs['ichnls'] = inputDeviceChannels

        self.server = pyo.Server(**kwargs)

        if outputDevice is not None:
            if isinstance(outputDevice, string_types):
                outputDevice = self.pa_output_device_by_name(
                    outputDevice)

            self.server.setOutputDevice(outputDevice)

        if inputDevice is not None:
            if isinstance(inputDevice, string_types):
                inputDevice = self.pa_input_device_by_name(
                    inputDevice)

            self.server.setInputDevice(inputDevice)

        if midiDevice is not None:
            if isinstance(midiDevice, string_types):
                midiDevice = self.pm_input_device_by_name(
                    midiDevice)

            self.server.setMidiInputDevice(midiDevice)

        self.server.boot()
        self.server.start()
        if not self.server.getIsBooted() or not self.server.getIsStarted():
            raise BootFailed()

        self.init_listeners()
        self.init_controls()
        self.init_synths()
        self.init_mixers()

    def init_log(self):
        self.log = logging.getLogger('%s.%s' % (
            __name__, self.__class__.__name__))

    def discover_devices(self):
        self.pa_inputs, self.pa_outputs = discover_pa_devices()
        self.pm_inputs = discover_pm_devices()

    def pa_input_device_by_name(self, want):
        '''Find a portaudio input device by name. Iterate over available
        devices, looking for first device with a matching prefix.'''
        want = want.lower()
        for index, info in self.pa_inputs.items():
            if info['name'].lower().startswith(want):
                return index

        raise MissingPAInputDevice(name)

    def pa_output_device_by_name(self, want):
        '''Find a portaudio output device by name. Iterate over available
        devices, looking for first device with a matching prefix.'''
        want = want.lower()
        for index, info in self.pa_outputs.items():
            if info['name'].lower().startswith(want):
                return index

        raise MissingPAOutputDevice(want)

    def pm_input_device_by_name(self, want):
        '''Find a portmidi device by name. Iterate over available
        devices, looking for first device with a matching prefix.'''
        want = want.lower()
        for index, name in self.pm_inputs.items():
            if name.lower().startswith(want):
                return index

        raise MissingPMInputDevice(want)

    def create_synth_sine(self):
        self.log.debug('creating sine synth')
        return pyo.Sine(mul=0, freq=[FREQ_C4, FREQ_C4])

    def create_synth_square_line(self):
        self.log.debug('creating square synth [lintable]')
        t = pyo.LinTable([(0, 1), (8192//2, 1),
                          ((8192//2), -1), (8191, -1)])
        return pyo.Osc(table=t,
                       mul=0,
                       freq=[FREQ_C4, FREQ_C4])

    def create_synth_square(self):
        self.log.debug('creating square synth [additive]')
        t = pyo.SquareTable(order=self.nharmonics, size=self.tsize)
        return pyo.Osc(table=t,
                       mul=0,
                       freq=[FREQ_C4, FREQ_C4])

    def create_synth_sawtooth_line(self):
        self.log.debug('creating sawtooth synth [lintable]')
        t = pyo.LinTable([(0, 1), (8191, -1)])
        return pyo.Osc(table=t,
                       mul=0,
                       freq=[FREQ_C4, FREQ_C4])

    def create_synth_sawtooth(self):
        self.log.debug('creating sawtooth synth [additive]')
        t = pyo.SawTable(order=self.nharmonics, size=self.tsize)
        return pyo.Osc(table=t,
                       mul=0,
                       freq=[FREQ_C4, FREQ_C4])

    def create_synth_triangle_line(self):
        self.log.debug('creating triangle synth [lintable]')
        t = pyo.LinTable([(0, 0), (8192//4, 1), (8192//2, 0),
                          (3*(8192//4), -1), (8191, 0)])
        return pyo.Osc(table=t,
                       mul=0,
                       freq=[FREQ_C4, FREQ_C4])

    def create_synth_triangle(self):
        self.log.debug('creating triangle synth [additive]')
        c = cycle([1, -1])
        l = [next(c)/(i*i) if i % 2 == 1 else 0
             for i in range(1, (2*self.nharmonics))]
        t = pyo.HarmTable(list=l, size=self.tsize)
        return pyo.Osc(table=t,
                       mul=0,
                       freq=[FREQ_C4, FREQ_C4])

    def create_synth_passthrough(self):
        self.log.debug('creating passthrough synth')
        i = pyo.Input()
        return pyo.Mix(i, voices=2, mul=0)

    def init_synths(self):
        self._synths = []
        self.log.debug('start init synths')

        for i, synth in enumerate(self.synths):
            self.log.debug('creating synth %d (%s)',
                           i, synth['type'])

            try:
                func = getattr(self, 'create_synth_%(type)s' % synth)
            except AttributeError:
                raise UnknownSynthType(synth)

            s = func()
            self._synths.append(s)

            if 'volume' in synth:
                self.register_midi_listener(
                    synth['volume'],
                    partial(self.ctrl_volume, i))

            if 'freq' in synth:
                self.register_midi_listener(
                    synth['freq'],
                    partial(self.ctrl_freq, i))

        for i, synth in enumerate(self._synths):
            self.log.debug('activating synth %d', i)
            synth.out()

        self.log.debug('done init synths')

    def init_listeners(self):
        self._listen = {}

        c = pyo.RawMidi(self.midi_handler)

        # apparently we need to store a reference to this or
        # it goes away when it falls out of scope.
        self._listener = c
        c.out()

    def init_controls(self):
        self.log.debug('start init controls')

        if 'play' in self.controls:
            self.register_midi_listener(
                self.controls['play'],
                self.ctrl_play)

        if 'stop' in self.controls:
            self.register_midi_listener(
                self.controls['stop'],
                self.ctrl_stop)

        self.log.debug('done init controls')

    def ctrl_play(self, value):
        self.log.info('starting all synths')
        if value:
            for synth in self._synths:
                synth.out()

    def ctrl_stop(self, value):
        self.log.info('stopping all synths')
        if value:
            for synth in self._synths:
                synth.stop()

    def init_mixer_device(self, tag, mixer, element, channel, control,
                          capture=False):
        self.log.debug('creating mixer tag = %s', tag)

        self._mixer[tag] = {
            'mixer': mixer,
            'element': element,
            'capture': capture,
            'channel': alsamixer.channel_id[channel],
            'range': element.get_volume_range(),
        }

        self.register_midi_listener(
            control,
            partial(self.ctrl_mixer, tag))

    def init_mixers(self):
        self._mixer = {}
        self.log.debug('start init mixers')

        for mixer_name, mixer in self.mixers.items():
            m = alsamixer.Mixer()
            try:
                m.attach(mixer_name)
            except RuntimeError:
                raise MissingALSADevice(mixer_name)

            m.load()
            for element_name, element in mixer.items():
                try:
                    e = alsamixer.Element(m, element_name)
                except IOError:
                    raise MissingALSADevice('%s.%s' % (
                        mixer_name, element_name))

                # create output device controls
                for channel, control in element.get('output', {}).items():
                    tag = '%s.%s.%s.out' % (
                        mixer_name,
                        element_name,
                        channel)

                    self.init_mixer_device(tag, m, e, channel, control)

                # create capture device controls
                for channel, control in element.get('capture', {}).items():
                    tag = '%s.%s.%s.in' % (
                        mixer_name,
                        element_name,
                        channel)

                    self.init_mixer_device(tag, m, e, channel, control,
                                           capture=True)

        self.log.debug('done init mixers')

    def ctrl_mixer(self, name, value):
        e = self._mixer[name]['element']
        channel = self._mixer[name]['channel']
        capture = self._mixer[name]['capture']
        minvol, maxvol = self._mixer[name]['range']

        volume = int(minvol + (value/127) * (maxvol-minvol))
        self.log.debug('mixer %s: set volume = %d (from %d)',
                       name, volume, value)

        e.set_volume(volume, channel, capture)
        self._mixer_lock.release()

    def ctrl_freq(self, synth, value):
        freq = calc_key_freq(value)
        self.log.info('%d: set freq = %f', synth, freq)
        self._synths[synth].setFreq(freq)

    def ctrl_volume(self, synth, value):
        vol = value / 127
        self.log.info('%d: set volume = %f', synth, vol)
        self._synths[synth].setMul(vol)

    def midi_handler(self, status, control, value):
        self.log.debug('midi control %d value %d', control, value)
        if control in self._listen:
            self._listen[control](value)

    def shutdown(self):
        self.log.info('shutting down sound server')
        self.server.shutdown()

    def register_midi_listener(self, control, func):
        self.log.debug('registering action for control %d', control)
        if control in self._listen:
            raise AlreadyListening(control)

        self._listen[control] = func

    def unregister_midi_listener(self, control):
        if control in self._listen:
            self.log.debug('unregistering action for control %d', control)
            del self._listen[control]
