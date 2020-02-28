import time
import timeit
import statistics


def fn():
    time.sleep(0.00005)


def perf(n):
    t = [0] * n
    for i in range(n):
        start = time.perf_counter()
        time.sleep(0.00005)
        end = time.perf_counter()
        elapsed = end - start
        t[i] = elapsed
    return t


def _timeit(n):
    timer = timeit.Timer(stmt=fn)
    t = timer.repeat(n, 1)
    return t


def stats(t):
    print("Min   ", statistics.mean(t))
    print("Max   ", statistics.mean(t))
    print("Mean  ", statistics.mean(t))
    print("Std   ", statistics.stdev(t))
    print("Median", statistics.median(t))


n = 10000
perf(n)
stats(perf(n))
print()
_timeit(n)
stats(_timeit(n))
