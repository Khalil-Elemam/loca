import argparse
import inspect
from importlib.metadata import version, PackageNotFoundError
from colorama import init, Fore, Style
from .core import commands


def main() -> None:
    init(autoreset=True)

    parser = argparse.ArgumentParser(
        prog="loca",
        description="Local, privacy-first semantic code search. Instantly find relevant functions, classes, and files in and python codebase using natural language queries. Powered by embeddings, syntax parsing, and vector search.",
    )

    try:
        __version__ = version("loca")
    except PackageNotFoundError:
        __version__ = "unknown"

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version of loca.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands: set-root, index, clear, query. Use -h after a command for details.",
    )

    set_root_subparser = subparsers.add_parser(
        name="set-root",
        help="Set the root directory of your project for all loca operations.",
        description="Set the root directory of your project for all loca operations. This directory will be used as the base for indexing and searching.",
    )
    set_root_subparser.add_argument(
        "--path",
        "-p",
        type=str,
        default=".",
        help="Path to the project root directory (default: current directory).",
    )

    index_subparser = subparsers.add_parser(
        name="index",
        help="Index your project’s Python files for fast semantic code search.",
        description="Scan and index all Python files in your project for semantic code search. Run this after setting the project root or when your code changes.",
    )

    clear_subparser = subparsers.add_parser(
        name="clear",
        help="Clear all loca caches and remove all indexed code from the database.",
        description="Clear all loca caches and remove all indexed code from the database. Use this if you want to reset the index or start fresh.",
    )

    query_subparser = subparsers.add_parser(
        name="query",
        help="Search your codebase using a natural language query.",
        description="Search your codebase using a natural language query. Returns the most relevant code snippets, functions, or classes.",
    )
    query_subparser.add_argument(
        "q",
        type=str,
        help="Your natural language search query.",
    )
    query_subparser.add_argument(
        "-n",
        "--n_results",
        type=int,
        default=5,
        help="Number of code results to display (default: 5).",
    )

    args = vars(parser.parse_args())
    command = commands.get(args.get("command"))

    if command is None:
        print(
            f"{Fore.RED}{Style.BRIGHT}No command provided or unknown command.{Style.RESET_ALL}\n"
        )
        parser.print_help()
        return

    sig = inspect.signature(command)
    accepted_args = sig.parameters.keys()
    command_args = {k: args.get(k) for k in accepted_args}
    command(**command_args)
