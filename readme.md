# C++ Massif & NanoBench Parser

This repo contains two Python scripts which compile and analyze C++ benchmarking tools
* **execution_analysis.py**: Given a directory of _n_ C++ source files, this script executes the nanobench benchmarking library to measure execution speed. The results are then compiled and _n_ bar charts are created.
* **memory_analysis.py**: Given a directory of _n_ C++ source files, this script compiles the code and executes the Valgrind Massif tool on all executables to measure heap and stack usage. The results are then parsed into _n_ line graphs. 

### Requirements:
- Python 3.7+
- Python packages: `pandas`, `matplotlib`
- A Linux or ARM system
- The ETL `/etl-18.1.3` directory in the user's home path
- The nanobench header file inside a `/nanobench_include` directory in the user's home path

### Usage
```shell script
chmod u+x parser
./parser directory
```
where `parser` is either `execution_analysis.py` or `memory_analysis.py` and `directory` is the path to the directory containing the `*.cpp` source files.

The intermediate directories and final output `png` file are located in the present working directory.