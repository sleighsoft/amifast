import benchit

stats = benchit.benchit(
    "sorted(s, key=f)", repetitions=2048, setup="f = lambda x: x; s = list(range(1000))"
)

# TODO
