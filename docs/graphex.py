#!/usr/bin/python

# This extracts doctest examples from the given document and, if they
# produce a 'waveform' variable, generates a graph of the waveform and
# saves it to a file.

import argparse
import logging
import matplotlib.pyplot as plt
from doctest import DocTestParser, Example

LOG = logging.getLogger(__name__)


def graph(exnum, ctx, output, width=None, height=None):
    '''Use matplotlib to graph the context of
    ctx['waveform'].'''

    global args
    LOG.info('graphing example %d', exnum)

    if 'waveform' not in ctx:
        LOG.warn('no waveform in example %d', exnum)
        return

    LOG.info('plotting waveform for example %d', exnum)
    kwargs = {}
    if width and height:
        kwargs['figsize'] = (width, height)
    elif width or height:
        raise ValueError('you must provide both width and height')

    fig = plt.figure(**kwargs)
    ax = fig.add_subplot(111)
    ax.plot(ctx['waveform'])
    fig.savefig(output % exnum)


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

    p.add_argument('--width', '-W',
                   type=int)
    p.add_argument('--height', '-H',
                   type=int)
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

    excount = 0
    ctx = {}
    for chunk in chunks:
        if isinstance(chunk, Example):
            exec chunk.source in ctx
            if 'waveform' in ctx:
                excount += 1
                graph(excount, ctx, args.output,
                      width=args.width, height=args.height)
                del ctx['waveform']

if __name__ == '__main__':
    main()
