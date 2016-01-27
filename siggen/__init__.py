#!/usr/bin/python

from __future__ import division

import argparse
import logging
import math
import mido
import numpy
import Queue as queue
import scipy.signal
import signal
import threading
import time
import yaml
from . import mute_alsa_errors  # NOQA
import pyaudio

LOG = logging.getLogger(__name__)
FREQ_A0 = 27.5
FREQ_C8 = 4186
QUIT = False

class Logger(object):
    def init_log(self):
        self.log = logging.getLogger('%s.%s' % (self.__class__.__name__,
                                                __name__))


class Passthru(threading.Thread, Logger):
    def __init__(self,
                 pa,
                 rate=44100):

        super(Passthru, self).__init__()

        self.init_log()

        self.volume = 1
        self.rate = rate
        self.q = queue.Queue()

        self.stream = pa.open(format=pyaudio.paFloat32,
                              channels=1,
                              rate=self.rate,
                              output=True,
                              input=True)

        self.play = threading.Event()
        self.quit = threading.Event()

    def run(self):
        self.log.info('starting main loop')

        while not self.quit.is_set():
            self.play.wait()
            self.stream.start_stream()

            while not self.quit.is_set() and self.play.is_set():
                try:
                    while True:
                        msg = self.q.get(False)
                        self.handle_msg(msg)
                except queue.Empty:
                    pass

                data = self.stream.read(1024)
#                data = numpy.fromstring(data, numpy.int16)
#                data = (data * self.volume).astype(numpy.int16).tostring()
                self.stream.write(data)

            self.stream.stop_stream()

            if self.quit.is_set():
                break

        self.log.info('exit main loop')

    def _set_volume(self, value):
        self.log.debug('setting volume to %d', value)
        self.volume = value

    def handle_msg(self, msg):
        if msg[0] == 'v':
            self._set_volume(msg[1])

    def ctrl_volume(self, value):
        volume = (value/127.0) * 2
        LOG.debug('%s request set volume to %d', self, volume)
        self.q.put(('v', volume))

    def ctrl_play(self):
        self.log.info('playing')
        self.play.set()

    def ctrl_pause(self):
        self.log.info('pausing')
        self.play.clear()

    def ctrl_mute(self, value):
        if value:
            self.ctrl_pause()
        else:
            self.ctrl_play()

    def ctrl_stop(self):
        self.log.info('setting quit flag')
        self.quit.set()
        # This wakes up any sleepers
        self.play.set()
        self.join()


class Synth(threading.Thread, Logger):
    def __init__(self,
                 pa,
                 rate=44100,
                 freq_low=FREQ_A0,
                 freq_high=FREQ_C8,
                 tuning=0):

        super(Synth, self).__init__()

        self.init_log()

        self.freq_low = freq_low
        self.freq_high = freq_high
        self.tuning = tuning

        self.volume = 0
        self.freq = freq_low
        self.rate = rate

        self.quit = threading.Event()
        self.play = threading.Event()
        self.q = queue.Queue()

        self.stream = pa.open(format=pyaudio.paFloat32,
                              channels=1,
                              rate=self.rate,
                              output=True)

    def calc_key(self, value):
        key = int((value/127.0) * 88)
        self.log.debug('got key = %d', key)
        freq = 2 ** ((key-49)/12) * 440
        self.log.info('freq control value %d -> key %d -> freq %f',
                      value, key, freq)
        return freq

    def waveform(self, rate, factor, period):
        return numpy.sin(numpy.arange(rate) * factor)[:period]

    def update_freq(self):
        period = int(self.rate/self.freq)
        factor = float(self.freq) * (math.pi * 2) / self.rate

        self._base_waveform = self.waveform(self.rate, factor, period)
        self.update_volume()

    def update_volume(self):
        self._active_waveform = (self._base_waveform * self.volume).astype(
            numpy.float32).tostring()

    def run(self):
        self.update_freq()
        self.log.info('starting main loop')

        while not self.quit.is_set():
            self.play.wait()
            self.stream.start_stream()

            while not self.quit.is_set() and self.play.is_set():
                try:
                    while True:
                        msg = self.q.get(False)
                        self.handle_msg(msg)
                except queue.Empty:
                    pass

                self.stream.write(self._active_waveform)

            self.stream.stop_stream()

            if self.quit.is_set():
                break

        self.log.info('exit main loop')

    def handle_msg(self, msg):
        if msg[0] == 'v':
            self._set_volume(msg[1])
        elif msg[0] == 'f':
            self._set_freq(msg[1])

    def _set_volume(self, value):
        self.log.debug('setting volume to %d', value)
        self.volume = value
        self.update_volume()

    def _set_freq(self, value):
        self.log.debug('setting frequency to %d', value)
        self.freq = value
        self.update_freq()

    def ctrl_play(self):
        self.log.info('playing')
        self.play.set()

    def ctrl_pause(self):
        self.log.info('pausing')
        self.play.clear()

    def ctrl_mute(self, value):
        if value:
            self.ctrl_pause()
        else:
            self.ctrl_play()

    def ctrl_stop(self):
        self.log.info('setting quit flag')
        self.quit.set()
        # This wakes up any sleepers
        self.play.set()
        self.join()

    def ctrl_volume(self, value):
        volume = (value/127.0) * 2
        LOG.debug('%s request set volume to %d', self, volume)
        self.q.put(('v', volume))

    def ctrl_freq(self, value):
        freq = self.calc_key(value)
        LOG.debug('%s request set freq to %f', self, freq)
        self.q.put(('f', freq))

    def __str__(self):
        return '<Synth "%s">' % self.__class__.__name__


class Sine(Synth):
    pass


class Square(Synth):
    def waveform(self, rate, factor, period):
        return scipy.signal.square(
            numpy.arange(rate) * factor)[:period]


class Triangle(Synth):
    def waveform(self, rate, factor, period):
        return scipy.signal.sawtooth(
            numpy.arange(rate) * factor, width=0.5)[:period]


class Sawtooth(Synth):
    def waveform(self, rate, factor, period):
        return scipy.signal.sawtooth(
            numpy.arange(rate) * factor)[:period]


def parse_args():
    p = argparse.ArgumentParser()
    g = p.add_argument_group('Logging options')
    g.add_argument('--verbose', '-v',
                   action='store_const',
                   const='INFO',
                   dest='loglevel')
    g.add_argument('--debug',
                   action='store_const',
                   const='DEBUG',
                   dest='loglevel')

    p.add_argument('--config', '-f',
                   default='signals.yml')

    p.set_defaults(loglevel='WARN')
    return p.parse_args()


def set_quit_flag(*args):
    global QUIT

    LOG.debug('setting global quit flag')
    QUIT = True


def main():
    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    with open(args.config) as fd:
        config = yaml.load(fd)

    dev = mido.open_input(config['device'])
    pa = pyaudio.PyAudio()

    synths = {
        'sine':  Sine(pa, rate=config['rate']),
        'square': Square(pa, rate=config['rate']),
        'triangle': Triangle(pa, rate=config['rate']),
        'sawtooth': Sawtooth(pa, rate=config['rate']),
    }

    controls = {}
    for synth in synths:
        controls[int(config[
            'controls'][synth]['freq'])] = synths[synth].ctrl_freq
        controls[int(config[
            'controls'][synth]['volume'])] = synths[synth].ctrl_volume
        controls[int(config[
            'controls'][synth]['mute'])] = synths[synth].ctrl_mute

        synths[synth].start()

    signal.signal(signal.SIGINT,
                  set_quit_flag)

    while not QUIT:
        for event in dev.iter_pending():
            LOG.debug('event: %s', event)
            if event.control in controls:
                controls[event.control](event.value)
            elif event.control == int(config['controls']['play']):
                if event.value:
                    for synth in synths:
                        synths[synth].ctrl_play()
            elif event.control == int(config['controls']['stop']):
                if event.value:
                    for synth in synths:
                        synths[synth].ctrl_pause()

        time.sleep(0.1)

    LOG.info('stopping all synths')
    for synth in synths:
        synths[synth].ctrl_stop()

    LOG.info('all done.')

if __name__ == '__main__':
    main()
