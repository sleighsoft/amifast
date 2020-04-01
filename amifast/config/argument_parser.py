import argparse
from typing import List
from typing import Tuple


class Parser(object):
    def __init__(self, usage=None):
        self._parser = BenchitParser(prog=None, usage=usage)

        self.add_argument("file_or_dir", nargs="*")

    def parse_known_args(self) -> argparse.Namespace:
        return self._parser.parse_known_args()[0]

    def parse_args(self) -> Tuple[argparse.Namespace, List[str]]:
        return self._parser.parse_known_args()

    def add_argument(self, *arg, **kwargs) -> None:
        self._parser.add_argument(*arg, **kwargs)


class BenchitParser(argparse.ArgumentParser):
    def __init__(self, prog=None, usage=None):
        super().__init__(prog=prog, usage=usage, add_help=False, allow_abbrev=False)


# TODO
