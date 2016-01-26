#!/usr/bin/python

from __future__ import division

import argparse
import ctypes
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

LOG = logging.getLogger(__name__)
FREQ_A0 = 27.5
FREQ_C8 = 4186
QUIT = False

#
# The following block of cruft supresses a variety of unhelpful
# warnings from ALSA.
#

ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                      ctypes.c_char_p, ctypes.c_int,
                                      ctypes.c_char_p)


def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = ctypes.cdll.LoadLibrary('libasound.so.2')
asound.snd_lib_error_set_handler(c_error_handler)

import pyaudio

class Synth(threading.Thread):
    def __init__(self,
                 pa,
                 rate=16000,
                 freq_low=FREQ_A0,
                 freq_high=FREQ_C8):

        super(Synth, self).__init__()

        self.init_log()

        self.freq_low = freq_low
        self.freq_high = freq_high

        self.volume = 0
        self.freq = 0
        self.rate = rate

        self.quit = threading.Event()
        self.play = threading.Event()
        self.q = queue.Queue()

        self.stream = pa.open(format=pyaudio.paFloat32,
                                 channels=1,
                                 rate=self.rate,
                                 output=True)

    def init_log(self):
        self.log = logging.getLogger('%s.%s' % (self.__class__.__name__,
                                                __name__))

    def generate(self):
        freq = self.freq_low + (self.freq/127.0) * (self.freq_high -
                                                    self.freq_low)
        period = int(self.rate/freq)

        volume = (self.volume/127.0)

        factor = float(freq) * (math.pi * 2) / self.rate
        chunk = numpy.sin(numpy.arange(self.rate) * factor)[:period]
        chunk = chunk * volume
        self.waveform = chunk.astype(numpy.float32).tostring()

    def run(self):
        self.generate()

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

                self.stream.write(self.waveform)

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
        self.log.info('setting volume to %d', value)
        self.volume = value
        self.generate()

    def _set_freq(self, value):
        self.log.info('setting frequency to %d', value)
        self.freq = value
        self.generate()

    def ctrl_play(self):
        self.log.info('setting play flag')
        self.play.set()

    def ctrl_pause(self):
        self.log.info('clearing play flag')
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
        self.volume = value
        self.generate()
        LOG.info('%s request set volume to %d', self, self.volume)

    def ctrl_freq(self, value):
        self.freq = value
        self.generate()
        LOG.info('%s request set freq to %d', self, self.freq)

    def __str__(self):
        return '<Synth "%s">' % self.__class__.__name__


class Sine(Synth):
    pass


class Square(Synth):
    def generate(self):
        freq = self.freq_low + (self.freq/127.0) * (self.freq_high -
                                                    self.freq_low)
        period = int(self.rate/freq)
        volume = (self.volume/127.0)

        factor = float(freq) * (math.pi * 2) / self.rate
        chunk = scipy.signal.square(numpy.arange(self.rate) * factor)[:period]
        chunk = chunk * volume
        self.waveform = chunk.astype(numpy.float32).tostring()


class Triangle(Synth):
    def generate(self):
        freq = self.freq_low + (self.freq/127.0) * (self.freq_high -
                                                    self.freq_low)
        period = int(self.rate/freq)
        volume = (self.volume/127.0)

        factor = float(freq) * (math.pi * 2) / self.rate
        chunk = scipy.signal.sawtooth(numpy.arange(self.rate) * factor,
                                      width=0.5)[:period]
        chunk = chunk * volume
        self.waveform = chunk.astype(numpy.float32).tostring()


class Sawtooth(Synth):
    def generate(self):
        freq = self.freq_low + (self.freq/127.0) * (self.freq_high -
                                                    self.freq_low)
        period = int(self.rate/freq)
        volume = (self.volume/127.0)

        factor = float(freq) * (math.pi * 2) / self.rate
        chunk = (scipy.signal.sawtooth(numpy.arange(self.rate)
                                       * factor)[:period])
        chunk = chunk * volume
        self.waveform = chunk.astype(numpy.float32).tostring()


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
        'sine':  Sine(pa),
        'square': Square(pa),
        'triangle': Triangle(pa),
        'sawtooth': Sawtooth(pa),
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
                for synth in synths:
                    synths[synth].ctrl_play()
            elif event.control == int(config['controls']['stop']):
                for synth in synths:
                    synths[synth].ctrl_pause()

        time.sleep(0.1)

    LOG.info('stopping all synths')
    for synth in synths:
        synths[synth].ctrl_stop()

    LOG.info('all done.')

if __name__ == '__main__':
    main()
