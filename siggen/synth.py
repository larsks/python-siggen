from __future__ import division

from six import string_types
from functools import partial
from pyalsa import alsamixer
import logging
import pyo

FREQ_A0 = 27.5
FREQ_C8 = 4186
FREQ_C4 = 261.626
DEFAULT_MIDI_DEVICE = 'nanoKONTROL2 MIDI 1'
LOG = logging.getLogger(__name__)


class SynthError(Exception):
    pass


class BootFailed(SynthError):
    pass


class MissingDevice(SynthError):
    pass


class MissingPAInputDevice(MissingDevice):
    pass


class MissingPAOutputDevice(MissingDevice):
    pass


class MissingPMInputDevice(MissingDevice):
    pass


def calc_key_freq(value):
    key = int((value/127.0) * 88)
    freq = 2 ** ((key-49)/12) * 440
    LOG.debug('freq control value %d -> key %d -> freq %f',
              value, key, freq)
    return freq


class Synth(object):
    synth_names = ['sine', 'square', 'triangle', 'sawtooth', 'passthrough']

    def __init__(self,
                 midiController=DEFAULT_MIDI_DEVICE,
                 outputDevice=None,
                 outputDeviceChannels=None,
                 inputDevice=None,
                 inputDeviceChannels=None,
                 controls=None,
                 mixers=None):

        self.init_log()

        self.controls = controls
        self.mixers = mixers
        self.inputDevice = inputDevice
        self.outputDevice = outputDevice
        self.midiController = midiController

        self.discover_devices()

        kwargs = {}
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

        if midiController is not None:
            if isinstance(midiController, string_types):
                midiController = self.pm_input_device_by_name(
                    midiController)

            self.server.setMidiInputDevice(midiController)

        self.server.boot()
        self.server.start()
        if not self.server.getIsBooted() or not self.server.getIsStarted():
            raise BootFailed()

        self.init_controls()
        self.init_mixer()
        self.init_synths()

    def init_log(self):
        self.log = logging.getLogger('%s.%s' % (
            __name__, self.__class__.__name__))

    def discover_devices(self):
        self.discover_pa_devices()
        self.discover_pm_devices()

    def discover_pa_devices(self):
        self.pa_inputs, self.pa_outputs = pyo.pa_get_devices_infos()

    def discover_pm_devices(self):
        inputs = pyo.pm_get_input_devices()
        self.pm_inputs = dict(zip(inputs[1], inputs[0]))

    def pa_input_device_by_name(self, name):
        for index, info in self.pa_inputs.items():
            if name in info['name']:
                return index

        raise MissingPAInputDevice(name)

    def pa_output_device_by_name(self, want):
        for index, info in self.pa_outputs.items():
            if want in info['name']:
                return index

        raise MissingPAOutputDevice(want)

    def pm_input_device_by_name(self, want):
        for index, name in self.pm_inputs.items():
            if want in name:
                return index

        raise MissingPMInputDevice(want)

    def create_synth_sine(self, name):
        self.log.debug('creating synth %s', name)
        self.synths[name] = pyo.Sine(mul=0,
                                     freq=[FREQ_C4, FREQ_C4])

    def create_synth_square(self, name):
        self.log.debug('creating synth %s', name)
        t = pyo.SquareTable()
        self.synths[name] = pyo.Osc(table=t,
                                    mul=0,
                                    freq=[FREQ_C4, FREQ_C4])

    def create_synth_sawtooth(self, name):
        self.log.debug('creating synth %s', name)
        t = pyo.SawTable()
        self.synths[name] = pyo.Osc(table=t,
                                    mul=0,
                                    freq=[FREQ_C4, FREQ_C4])

    def create_synth_triangle(self, name):
        self.log.debug('creating synth %s', name)
        self.create_synth_sawtooth('triangle')

    def create_synth_passthrough(self, name):
        self.log.debug('creating synth %s', name)
        i = pyo.Input()
        self.synths[name] = pyo.Mix(i, voices=2, mul=0)

    def init_synths(self):
        self.synths = {}
        for synth in self.synth_names:
            func = getattr(self, 'create_synth_%s' % synth, None)
            if func is not None:
                func(synth)

        for synth in self.synths:
            self.log.debug('activating synth %s', synth)
            self.synths[synth].out()

    def init_controls(self):
        self._ctrl = {}

        for synth in self.synth_names:
            if 'volume' in self.controls[synth]:
                self._ctrl[self.controls[synth]['volume']] = (
                    partial(self.ctrl_volume, synth))
            if 'freq' in self.controls[synth]:
                self._ctrl[self.controls[synth]['freq']] = (
                    partial(self.ctrl_freq, synth))

        c = pyo.RawMidi(self.midi_handler)
        self._ctrl['raw'] = c
        c.out()

    def init_mixer(self):
        pass

    def ctrl_mixer(self, name, value):
        pass

    def ctrl_freq(self, synth, value):
        freq = calc_key_freq(value)
        self.log.info('%s: set freq = %f', synth, freq)
        self.synths[synth].setFreq(freq)

    def ctrl_volume(self, synth, value):
        vol = value / 127
        self.log.info('%s: set volume = %f', synth, vol)
        self.synths[synth].setMul(vol)

    def midi_handler(self, status, control, value):
        self.log.debug('midi control %d value %d', control, value)
        if control in self._ctrl:
            self._ctrl[control](value)
