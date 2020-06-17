#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import sys

import pandas
from matplotlib import pyplot

from utils import get_base_name, create_chart, get_arg, Color


def build_executable(source: str, dest: str):
    """
    Compiles and builds a single *.cpp file with a dependency on ETL via g++,
    and makes the produced object executable
    """
    print(f"-> Building {source}...", end='')

    home = os.path.expanduser('~')

    subprocess.run(
        ["/usr/bin/g++", source, "-std=c++17", "-isystem", home + "/etl-18.1.3/include", "-o", dest],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    os.chmod(path=dest, mode=0o555)

    print(" Done")


def run_massif(source: str, dest: str):
    """
    Runs Valgrind Massif on the provided executable and stores the result in the path specified by `dest`.
    Uses `--time-unit=B` and `--stacks` command line arguments for Massif.
    """
    print(f"-> Running massif on {source}...", end='')

    subprocess.run(
        ["valgrind", "--tool=massif", "--massif-out-file=" + dest, "--time-unit=B", "--stacks=yes", source],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print(" Done")


def convert_to_csv(source: str, dest: str):
    """
    Parses a Valgrind Massif output file and converts it into a CSV file, with `time, heap`, and `stack` column headers.
    Rows which have any field equal to 0 are removed.
    """
    print(f"-> Parsing {source}...", end='')
    with open(source, mode='r') as f:
        text = f.read()

    with open(dest, mode='w') as out:
        out.write("time,heap,stack\n")

        for match in regex.finditer(text):
            (time, heap, _, stack) = match.groups()
            out.write(f"{time},{heap},{stack}\n")

        out.write("\n")

    print(" Done")


def add_subplot(source: str, ax: pyplot.Axes):
    """
    Generates a logarithmic line graph from the provided CSV data file onto the specified subplot Axes.
    The subplot plots heap and stack usage against time, as well as an average line.
    """
    print(f"-> Creating chart from {source}...", end='')

    df = pandas.read_csv(source, header=0)

    for color, label in zip(Color, ['heap', 'stack']):
        ax.axhline(y=df[label].median(), color='0.75')
        ax.plot(df['time'], df[label], label=label, color=color.value)

    ax.set_yscale('log')
    ax.set_ylabel("bytes allocated")
    ax.set_xlabel("time (bytes)")

    print(" Done")


def collate_stats(source: str, dest: str):
    """
    Collects various stats from the CSV file located at `source`, including the median, min, max, and std dev
    """
    print(f"-> Collecting statistics from {source}...", end='')

    df = pandas.read_csv(source, header=0)

    with open(dest, mode='a') as f:
        f.write('\n' + get_base_name(source) + '\n')

    stats = {}
    for label in ['heap', 'stack']:
        col = df[label]
        stats[label] = [col.median(), col.min(), col.max(), col.std()]

    stats_df = pandas.DataFrame(data=stats, index=['median', 'min', 'max', 'stdev'])
    stats_df.to_csv(dest, mode='a')

    print("Done")


def process():
    print("\nBuilding files...")
    for path in os.listdir(cpp_dir):
        build_executable(f"{cpp_dir}/{path}", f"{generated_dir}/{get_base_name(path)}")

    print("\nRunning massif...")
    for path in os.listdir(generated_dir):
        run_massif(f"{generated_dir}/{path}", f"{massif_dir}/{get_base_name(path)}.txt")

    print("\nParsing...")
    for path in os.listdir(massif_dir):
        convert_to_csv(f"{massif_dir}/{path}", f"{csv_dir}/{get_base_name(path)}.csv")

    print("\nWriting stats...")
    for path in os.listdir(csv_dir):
        collate_stats(path, stats_path)

    print("\nCreating subplots...")

    create_chart(csv_dir=csv_dir, chart_path=chart_path, subplot_builder=add_subplot, title_suffix=suffix)

    print(" Done")


memory_dir = os.getcwd() + "/memory_benchmark"
cpp_dir = sys.argv[1]
suffix = get_arg('--suffix')

generated_dir = memory_dir + "/generated"
massif_dir = memory_dir + "/massif"
csv_dir = memory_dir + "/csv"
stats_path = memory_dir + "/stats.csv"
chart_path = memory_dir + "/chart.png"

os.remove(stats_path)

regex = re.compile("time=(\\d+)\nmem_heap_B=(\\d+)\nmem_heap_extra_B=(\\d+)\nmem_stacks_B=(\\d+)")

shutil.rmtree(memory_dir, ignore_errors=True)
os.mkdir(memory_dir)

for directory in [generated_dir, massif_dir, csv_dir]:
    os.mkdir(directory)

process()

print("\nComplete.")
