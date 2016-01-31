#!/usr/bin/python

import logging
import time
import yaml
from . import synth


LOG = logging.getLogger()
QUIT = False


class Logger(object):
    def init_log(self):
        self.log = logging.getLogger('%s.%s' % (self.__class__.__name__,
                                                __name__))


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

    p.add_argument('--wait', '-w',
                   action='store_true',
                   help='wait for devices instead of failing')

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

    if midiDevice:
        kwargs['midiDevice'] = midiDevice['name']

    while True:
        try:
            s = synth.Synth(
                controls=config['controls'],
                mixers=config['mixers'],
                **kwargs)
            break
        except synth.MissingDevice as err:
            if args.wait:
                LOG.warn('waiting for %s', err)
            else:
                raise

    LOG.warn('siggen ready')
    while not QUIT:
        time.sleep(0.5)

    s.stop()
    LOG.warn('all done.')

if __name__ == '__main__':
    main()
