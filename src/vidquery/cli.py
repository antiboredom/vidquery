import argparse
import os
from rich.console import Console
from rich.table import Table
from . import vidquery
from . import gui


def listvideos():
    table = Table(title="Videos", show_lines=True, header_style="bold red")

    table.add_column("Name")
    table.add_column("Full Path")
    table.add_column("Parsed")

    vids = vidquery.get_videos()
    parsers = vidquery.get_video_parsers()
    vidspans = {}
    for parser in parsers:
        print(parser)
        vid_id, parser_id, name, cat, subcat = parser
        if vid_id not in vidspans:
            vidspans[vid_id] = []
        vidspans[vid_id].append(f"{subcat} ({name})")

    for v in vids:
        parsed = None
        if v.id in vidspans:
            parsed = ", ".join(vidspans[v.id])
        table.add_row(os.path.basename(v.path), v.path, parsed)

    console = Console()
    console.print(table)


def listparsers():
    table = Table(title="Parser Plugins", show_lines=True, header_style="bold red")

    table.add_column("Name")
    table.add_column("Label", justify="left", no_wrap=True)
    table.add_column("Category", justify="left")
    table.add_column("Description", justify="left", no_wrap=False)

    for k, v in vidquery.get_installed_parsers().items():
        table.add_row(v["long_name"], k, v["cat"], v["description"])
    console = Console()
    console.print(table)


def cli():
    parser = argparse.ArgumentParser(
        description="Analyze and search videos for dialog, objects, scenes, and more."
    )

    parser.add_argument(
        "--gui", required=False, action="store_true", help="Open the graphic interface."
    )

    parser.add_argument("--search", "-s", required=False, help="Search through videos.")

    parser.add_argument("--analyze", "-a", required=False, help="Analyze videos.")

    parser.add_argument(
        "--input",
        "-i",
        dest="input",
        nargs="*",
        required=False,
        help="Video file or files.",
    )

    parser.add_argument(
        "--listvideos",
        "-lv",
        required=False,
        action="store_true",
        default=False,
        help="List all videos.",
    )

    parser.add_argument(
        "--listparsers",
        "-lp",
        help="List all parser plugins.",
        required=False,
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    if args.listparsers:
        listparsers()

    if args.listvideos:
        listvideos()

    if args.gui:
        gui.gui()

    if args.search:
        input = []
        if args.input:
            input = args.input
        results = vidquery.search(args.search, input)
        if results is None:
            print("no results found")
        else:
            for r in results:
                print(f"{r.video.path}: {r.start} -> {r.end} {r.content}")

    if args.analyze and args.input:
        if args.analyze == "all":
            for parser in vidquery.get_installed_parsers():
                print("Analyzing", parser)
                vidquery.analyze(parser, args.input)
        else:
            print("Analyzing", args.analyze)
            vidquery.analyze(args.analyze, args.input)


if __name__ == "__main__":
    cli()
