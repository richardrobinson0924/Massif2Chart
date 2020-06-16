#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

import pandas
from matplotlib import pyplot

from utils import get_base_name, create_chart, get_arg, colors


def build_executable(source: str, dest: str):
    """
    Compiles and builds a single *.cpp file with dependencies on ETL and nanobench via g++,
    and makes the produced object executable
    """
    print(f"-> Building {source}...", end='')

    home = os.path.expanduser('~')

    subprocess.run([
        "g++", source, home + "/nanobench.cpp", "-isystem", home + "/nanobench_include", "-isystem",
        home + "/etl-18.1.3/include", "-std=c++17", "-o", dest
    ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    os.chmod(path=dest, mode=0o555)

    print(" Done")


def run_benchmark(source: str, dest: str):
    """
    Runs Valgrind Massif on the provided executable and stores the result in the path specified by `dest`.
    Uses `--time-unit=B` and `--stacks` command line arguments for Massif.
    """
    print(f"-> Executing benchmark {source}...", end='')

    with open(dest, 'w') as out:
        subprocess.run(source, stdout=out)

    print(" Done")


def add_subplot(source: str, ax: pyplot.Axes):
    print(f"-> Creating chart from {source}...", end='')

    df = pandas.read_csv(source, header=0, sep=';')
    df[['library', 'function']] = df.name.str.split('_', expand=True, n=1)
    df = df.pivot('function', 'library', 'elapsed')

    normalized = df.div(df.max(axis=1), axis=0)
    normalized.plot(ax=ax, kind='bar', color=colors)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend(loc='upper left')
    ax.set_ylabel('execution time, normalized')
    ax.set_title(get_base_name(source) + suffix)

    print(" Done")


def process():
    print("\nBuilding files...")
    for path in os.listdir(cpp_dir):
        build_executable(f"{cpp_dir}/{path}", f"{generated_dir}/{get_base_name(path)}")

    print("\nExecuting benchmarks...")
    for path in os.listdir(generated_dir):
        run_benchmark(f"{generated_dir}/{path}", f"{csv_dir}/{get_base_name(path)}.csv")

    print("\nCreating subplots...")

    create_chart(csv_dir=csv_dir, chart_path=chart_path, subplot_builder=add_subplot)

    print(" Done")


benchmark_dir = os.getcwd() + "/execution_time_benchmark"
cpp_dir = sys.argv[1]
suffix = get_arg('--suffix')

generated_dir = benchmark_dir + "/generated"
massif_dir = benchmark_dir + "/massif"
csv_dir = benchmark_dir + "/csv"
chart_path = benchmark_dir + "/chart.png"

shutil.rmtree(benchmark_dir, ignore_errors=True)
os.mkdir(benchmark_dir)

for directory in [generated_dir, csv_dir]:
    os.mkdir(directory)

process()

print("\nComplete.")
