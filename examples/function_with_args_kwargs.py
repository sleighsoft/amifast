import random
import time

import amifast


# ================================ DECORATOR ================================ #

# 1. Use decorators on a function that we want to benchmark
#   (from bottom to top)
#   1. Benchmark it 2 times
#   2. Convert stats to CSV
#   3. Save converted stats to decorator_vs_functional.csv


@amifast.d_benchit(2)
def wait_a_moment(a_moment, another_moment=0.05):
    time.sleep(a_moment + another_moment)


# 2. Run our function a couple of times to get multiple rows in our csv
run1 = wait_a_moment(0.1)
run2 = wait_a_moment(0.4, another_moment=0.025)
run3 = wait_a_moment(0.9)

# 3. Check how long it took on average
print(run1.mean)
print(run2.mean)
print(run3.mean)


# ================================ FUNCTIONAL =============================== #


def wait_a_moment_2(a_moment, another_moment=0.05):
    time.sleep(a_moment + another_moment)


# 1. Benchmark it 2 times
stats = benchit.benchit(
    wait_a_moment_2, 2, fn_args=(1.2,), fn_kwargs={"another_moment": 0.1}
)
# 2. Check how long it took on average
print(stats.mean)
