#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

import pandas
from matplotlib import pyplot

from utils import get_base_name, create_chart


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
    normalized.plot(ax=ax, kind='bar')

    ax.set_ylabel('execution time, normalized')
    ax.set_title(get_base_name(source))

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


wd = os.getcwd()
cpp_dir = sys.argv[1]

generated_dir = wd + "/generated_benchmark"
csv_dir = wd + "/csv_benchmark"
chart_path = wd + "/chart_benchmark.png"

for directory in [generated_dir, csv_dir]:
    shutil.rmtree(directory, ignore_errors=True)
    os.mkdir(directory)

process()

print("\nComplete.")
