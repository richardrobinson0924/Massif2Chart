import os
import sys
from math import sqrt, ceil

from matplotlib import pyplot
from typing import Callable


colors = ['blue', 'purple']


def get_arg(flag: str, default: str = '') -> str:
    """
    Finds and returns the command line argument associated with the specified `flag`,
    or `default` if the flag is not found.

    :param flag: the command line flag to attempt to find
    :param default: the string to return if `flag` does not exist
    :return: the command line argument following `flag`, or `default` if the flag does not exist
    """
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def get_base_name(path: str) -> str:
    """
    Given a fully qualified path name, returns the base name without the extension

    :param path: a fully qualified path, such as `/path/to/foo.ext`
    :return: the path's base name excluding extension, such as `foo`
    """
    base = os.path.basename(path)
    return os.path.splitext(base)[0]


def get_optimal_dims(x: int) -> (int, int):
    """
    Creates a grid with `n` rows and `m` cols such that `n` and `m` are minimized given `x` total elements

    :param x: then number of elements
    :return: (rows, cols)
    """
    return int(round(sqrt(x))), int(ceil(sqrt(x)))


def create_chart(csv_dir: str, chart_path: str, subplot_builder: Callable[[str, pyplot.Axes], None]):
    """
    Creates a chart with each subplot corresponding to a CSV data file in `csv_dir`. Each subplot is constructed via
    `subplot_builder`. The chart is then exported as a .png image to the path specified by `chart_path`

    :param chart_path: the fully-qualified path name to the generated .png image
    :param csv_dir: a directory exclusively containing data files formatted for this program
    :param subplot_builder: a function whose signature is `(str, pyplot.Axes) -> None`
    """
    dir_iter = os.listdir(csv_dir)
    rows, cols = get_optimal_dims(len(dir_iter))

    fig, axs = pyplot.subplots(nrows=rows, ncols=cols, figsize=(15, 10), sharey='all', squeeze=False)

    for i in range(len(dir_iter)):
        subplot_builder(f"{csv_dir}/{dir_iter[i]}", axs.flat[i])

    print("\nBuilding graph...", end='')
    pyplot.tight_layout()
    pyplot.xticks(rotation=45, ha='right')

    fig.savefig(chart_path, dpi=100)
