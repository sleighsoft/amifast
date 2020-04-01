"""
command line options
"""
from collectors.file_system_collector import FSCollector
from config.argument_parser import Parser


def main():
    """Application entry point. Also used to generate `benchit.exe`.
    """
    parser = Parser(usage="%(prog)s [file_or_dir] [file_or_dir] [...]")
    cmd_args = parser.parse_known_args()
    # TODO
    raise NotImplementedError("benchit cmd coming in the future")
