import argparse
import os

import pandas
from matplotlib import pyplot

colors = ['tab:purple', 'tab:blue']


def memory_plot_builder(data: str, ax: pyplot.Axes):
    df = pandas.read_csv(data, header=0)

    for color, label in zip(colors, ['heap', 'stack']):
        ax.axhline(y=df[label].median(), color='0.75')
        ax.plot(df['time'], df[label], label=label, color=color)

    ax.set_yscale('log')
    ax.set_ylabel("bytes allocated")
    ax.set_xlabel("time (bytes)")


def performance_plot_builder(data: str, ax: pyplot.Axes):
    df = pandas.read_csv(data, header=0, sep=';')
    df[['library', 'function']] = df.name.str.split('_', expand=True, n=1)
    df = df.pivot('function', 'library', 'elapsed')

    normalized = df.div(df.max(axis=1), axis=0)
    normalized.plot(ax=ax, kind='bar', color=colors)

    size = len(ax.patches) // 2
    for v_etl, v_stl, p_etl, p_stl in zip(df['etl'], df['stl'], ax.patches[:size], ax.patches[size:]):
        p, v = (p_etl, v_etl) if v_etl > v_stl else (p_stl, v_stl)

        x = p.get_x() + 0.18 * p.get_width()
        y = p.get_height() - 0.175
        ax.text(x=x, y=y, s=f'{v:.1E}', rotation=90, color='white')

    ax.set_ylabel('execution time (normalized)')


def parse_args() -> dict:
    parser = argparse.ArgumentParser()

    parser.add_argument('--mode', choices=['performance', 'memory'], required=True)
    parser.add_argument('input')
    parser.add_argument('--suffix', default='')
    parser.add_argument('--output', required=True)

    return vars(parser.parse_args())


args = parse_args()

for base in os.listdir(args['input']):
    path = args['input'] + '/' + base
    fig, axes = pyplot.subplots(figsize=(11, 5))

    if args['mode'] == 'performance':
        performance_plot_builder(path, axes)
    elif args['mode'] == 'memory':
        memory_plot_builder(path, axes)

    axes.legend(loc='lower left')
    axes.set_title(base + ' ' + args['suffix'])
    axes.set_xticklabels(axes.get_xticklabels(), rotation=45, ha='right')

    pyplot.tight_layout()
    out = f"{args['output']}/{base}.png"
    fig.savefig(out, dpi=300)

    print('-> ' + out)
