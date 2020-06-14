#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import sys
from math import sqrt, ceil

import pandas
from matplotlib import pyplot


def get_base_name(path: str) -> str:
    base = os.path.basename(path)
    return os.path.splitext(base)[0]


def get_optimal_dims(n: int) -> (int, int):
    return int(round(sqrt(n))), int(ceil(sqrt(n)))


def build_executable(source: str, dest: str):
    print(f"-> Building {source}...", end='')

    subprocess.run(
        ["/usr/bin/g++", source, "-std=c++17", "-isystem", "/home/pi/etl-18.1.3/include", "-o", dest],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    os.chmod(path=dest, mode=0o555)

    print(" Done")


def run_massif(source: str, dest: str):
    print(f"-> Running massif on {source}...", end='')

    subprocess.run(
        ["valgrind", "--tool=massif", "--massif-out-file=" + dest, "--time-unit=B", "--stacks=yes", source],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print(" Done")


def convert_to_csv(source: str, dest: str):
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


def create_chart(source: str, ax: pyplot.Axes):
    print(f"-> Creating chart from {source}...", end='')

    df = pandas.read_csv(source, header=0)
    ax.plot(df['time'], df['heap'], label='heap')
    ax.plot(df['time'], df['stack'], label='stack')

    ax.set_yscale('log')
    ax.set_ylabel("bytes allocated")
    ax.set_xlabel("time (bytes)")
    ax.legend()
    ax.set_title(get_base_name(source))

    print(" Done")


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

    print("\nCreating charts...")

    dir_iter = os.listdir(csv_dir)
    rows, cols = get_optimal_dims(len(dir_iter))

    fig, axs = pyplot.subplots(nrows=rows, ncols=cols, figsize=(15, 10), sharey='all')

    for i in range(len(dir_iter)):
        create_chart(f"{csv_dir}/{dir_iter[i]}", axs.flat[i])

    pyplot.tight_layout()
    fig.savefig(chart_path, dpi=100)


wd = sys.argv[1]
cpp_dir = sys.argv[2]

generated_dir = wd + "/generated"
massif_dir = wd + "/massif"
csv_dir = wd + "/csv"
chart_path = wd + "/chart.png"

regex = re.compile("time=(\\d+)\nmem_heap_B=(\\d+)\nmem_heap_extra_B=(\\d+)\nmem_stacks_B=(\\d+)")

for directory in [generated_dir, massif_dir, csv_dir]:
    shutil.rmtree(directory, ignore_errors=True)
    os.mkdir(directory)

process()

print("\nDone")
