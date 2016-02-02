#!/usr/bin/python

import argparse
import logging
import matplotlib.pyplot as plt
from doctest import DocTestParser, Example

LOG = logging.getLogger(__name__)


def graph(exnum, source):
    global args
    ctx = {}
    LOG.info('running example %d', exnum)
    exec source in ctx

    if 'waveform' not in ctx:
        LOG.warn('no waveform in example %d', exnum)
        return

    LOG.info('plotting waveform for example %d', exnum)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(ctx['waveform'])
    fig.savefig(args.output % exnum)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--verbose', '-v',
                   action='store_const',
                   const='INFO',
                   dest='loglevel')
    p.add_argument('--debug', '-d',
                   action='store_const',
                   const='DEBUG',
                   dest='loglevel')

    p.add_argument('--width', '-W')
    p.add_argument('--height', '-H')
    p.add_argument('--output', '-o',
                   default='example%d.svg')

    p.add_argument('input')

    p.set_defaults(loglevel='WARN')
    return p.parse_args()


def main():
    global args

    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    parser = DocTestParser()
    with open(args.input) as fd:
        chunks = parser.parse(fd.read())

    cur = []
    excount = 0
    for chunk in chunks:
        if isinstance(chunk, Example):
            cur.append(chunk.source)
            if chunk.source.startswith('waveform'):
                excount += 1
                source = ''.join(cur)
                cur = []
                graph(excount, source)

if __name__ == '__main__':
    main()

