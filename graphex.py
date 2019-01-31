#!/usr/bin/python

# This extracts doctest examples from the given document and, if they
# provide a specific target variable, produces plots of the contents of
# that variable using matplotlib.

import argparse
import logging
import matplotlib.pyplot as plt
from doctest import DocTestParser, Example

LOG = logging.getLogger(__name__)


def graph(exnum, ctx, var, output, width=None, height=None):
    '''Use matplotlib to graph the context of
    ctx[var].'''

    global args
    LOG.info('graphing example %d', exnum)

    if var not in ctx:
        LOG.warn('no data in example %d', exnum)
        return

    LOG.info('plotting data from example %d', exnum)
    kwargs = {}
    if width and height:
        kwargs['figsize'] = (width, height)
    elif width or height:
        raise ValueError('you must provide both width and height')

    fig = plt.figure(**kwargs)
    ax = fig.add_subplot(111)
    ax.plot(ctx[var])
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
    p.add_argument('var')

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
            exec(chunk.source, ctx)
            if args.var in ctx:
                excount += 1
                graph(excount, ctx, args.var, args.output,
                      width=args.width, height=args.height)
                del ctx[args.var]


if __name__ == '__main__':
    main()
