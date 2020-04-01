import os
import random
import time

import benchit

# ------ Clear file if it exists ------ #

if os.path.exists("decorator_vs_functional.csv"):
    os.remove("decorator_vs_functional.csv")


# ================================ DECORATOR ================================ #

# 1. Use decorators on a function that we want to benchmark
#   (from bottom to top)
#   1. Benchmark it 10 times
#   2. Convert stats to CSV
#   3. Save converted stats to decorator_vs_functional.csv


@benchit.d_save("decorator_vs_functional.csv")
@benchit.d_stats_as("csv")
@benchit.d_benchit(10)
def wait_a_moment():
    time.sleep(random.random() / 100)


# 2. Run our function a couple of times to get multiple rows in our csv
wait_a_moment()
wait_a_moment()
wait_a_moment()


# ================================ FUNCTIONAL =============================== #


def wait_a_moment_2():
    time.sleep(random.random() / 100)


# 1. Benchmark it 10 times
stats = benchit.benchit(wait_a_moment_2, 10)
# 2. Convert stats to CSV
as_csv = benchit.stats_as(stats, "csv")
# 3. Save converted stats to decorator_vs_functional.csv
as_csv.save("decorator_vs_functional.csv")
