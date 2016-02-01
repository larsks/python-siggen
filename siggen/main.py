#!/usr/bin/python

import argparse
import logging
import time
import yaml
import signal
from . import mute_alsa  # NOQA
from . import synth


LOG = logging.getLogger()
QUIT = False


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

    p.add_argument('--nomidi',
                   action='store_true',
                   help=argparse.SUPPRESS)

    p.add_argument('--list', '-l',
                   action='store_true',
                   help='list available devices')

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

    if args.list:
        pa_inputs, pa_outputs = synth.discover_pa_devices()
        pm_inputs = synth.discover_pm_devices()

        print 'Audio inputs:'
        for i, dev in pa_inputs.items():
            print '[%4d] %s' % (i, dev['name'])

        print
        print 'Audio outputs:'
        for i, dev in pa_outputs.items():
            print '[%4d] %s' % (i, dev['name'])

        print
        print 'MIDI inputs:'
        for i, dev in pm_inputs.items():
            print '[%4d] %s' % (i, dev)

        return

    with open(args.config) as fd:
        config = yaml.load(fd)

    kwargs = {}
    inputDevice = config.get('devices', {}).get('input')
    outputDevice = config.get('devices', {}).get('output')
    midiDevice = config.get('devices', {}).get('midi')

    if inputDevice:
        kwargs['inputDevice'] = inputDevice['name']
        kwargs['inputDeviceChannels'] = inputDevice.get('channels')

    if outputDevice:
        kwargs['outputDevice'] = outputDevice['name']
        kwargs['outputDeviceChannels'] = outputDevice.get('channels')

    if midiDevice and not args.nomidi:
        kwargs['midiDevice'] = midiDevice['name']

    s = synth.Synth(
        controls=config['controls'],
        mixers=config['mixers'],
        **kwargs)

    signal.signal(signal.SIGINT, set_quit_flag)

    LOG.warn('siggen ready')
    while not QUIT:
        time.sleep(0.5)

    s.shutdown()
    LOG.warn('all done.')

if __name__ == '__main__':
    main()
