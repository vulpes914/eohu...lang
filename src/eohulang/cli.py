from __future__ import annotations

import argparse
import sys

from .language import EohulangError, compile_bf_to_eohulang, read_source, run_program


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eohulang", description="Run 어흐랭 programs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an 어흐랭 source file.")
    run_parser.add_argument("path", help="Path to the source file.")
    run_parser.add_argument(
        "--input",
        default="",
        help="Input text fed to 꼴, / 어흐,,, instructions.",
    )

    bf_parser = subparsers.add_parser(
        "compile-bf", help="Translate a Brainfuck source file into 어흐랭."
    )
    bf_parser.add_argument("path", help="Path to the Brainfuck source file.")

    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            output = run_program(read_source(args.path), input_text=args.input)
            sys.stdout.write(output)
            return 0

        if args.command == "compile-bf":
            program = read_source(args.path)
            sys.stdout.write(compile_bf_to_eohulang(program))
            return 0
    except EohulangError as exc:
        parser.exit(1, f"error: {exc}\n")

    parser.exit(2, "error: unknown command\n")


if __name__ == "__main__":
    raise SystemExit(main())
