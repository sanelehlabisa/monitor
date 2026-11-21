"""Initialize and check the local research workspace without network requests."""

import argparse
import math
from pathlib import Path
import sys
from tempfile import TemporaryFile
from urllib.parse import urlsplit


WORKSPACE = Path(__file__).resolve().parent
SEED_TEMPLATE = (
    "# One public HTTP(S) starting URL per line.\n"
    "# Blank lines and lines beginning with # are ignored.\n"
)


def nonnegative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def positive_int(value: str) -> int:
    number = nonnegative_int(value)
    if number == 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def positive_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return number


def workspace_path(value: str) -> Path:
    """Resolve relative to the script and reject paths outside this experiment."""
    path = (WORKSPACE / value).resolve()
    if path == WORKSPACE or not path.is_relative_to(WORKSPACE):
        raise ValueError("Seed and output paths must be inside this experiment.")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Crawling, document reading and LM Studio integration are later tickets.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--init", action="store_true", help="create missing private folders and seed template")
    mode.add_argument("--check", action="store_true", help="check folders, write access and seed syntax offline")
    parser.add_argument("--seeds", default="links.txt", help="seed file, relative to this experiment")
    parser.add_argument("--data-dir", default="data", help="private output directory, inside this experiment")
    parser.add_argument("--max-depth", type=nonnegative_int, default=2, help="future crawl depth limit")
    parser.add_argument("--max-pages-per-seed", type=positive_int, default=50, help="future per-seed page limit")
    parser.add_argument("--max-requests", type=positive_int, default=200, help="future per-run request limit")
    parser.add_argument("--request-timeout", type=positive_float, default=15.0, help="future request timeout in seconds")
    parser.add_argument("--delay", type=positive_float, default=1.0, help="future delay between requests in seconds")
    return parser


def initialize(directories: list[Path], seeds: Path) -> None:
    if seeds.exists() and not seeds.is_file():
        raise ValueError("The seed path must be a file.")
    for directory in [*directories, seeds.parent]:
        directory.mkdir(parents=True, exist_ok=True)
    try:
        with seeds.open("x", encoding="utf-8", newline="\n") as output:
            output.write(SEED_TEMPLATE)
        print("Created a comment-only seed template; add starting URLs before crawling.")
    except FileExistsError:
        if not seeds.is_file():
            raise ValueError("The seed path must be a file.") from None
        print("Existing seed file preserved.")
    print("Private workspace initialized. Run --check to inspect it offline.")


def check_workspace(directories: list[Path], seeds: Path) -> bool:
    ready = True
    for directory in directories:
        label = directory.relative_to(WORKSPACE)
        if not directory.is_dir():
            print(f"Missing directory: {label}. Run --init.")
            ready = False
            continue
        try:
            with TemporaryFile(dir=directory) as probe:
                probe.write(b"workspace write check\n")
                probe.flush()
        except OSError:
            print(f"Directory is not writable: {label}.")
            ready = False

    if not seeds.is_file():
        print("Seed file missing. Run --init or use --seeds with an existing file.")
        return False
    try:
        with seeds.open(encoding="utf-8-sig") as source:
            lines = [(number, line.strip()) for number, line in enumerate(source, 1)]
    except UnicodeError:
        print("Seed file must be UTF-8 text.")
        return False

    count = 0
    invalid_lines: list[int] = []
    for number, seed in lines:
        if not seed or seed.startswith("#"):
            continue
        count += 1
        try:
            parsed = urlsplit(seed)
            valid = (
                parsed.scheme in {"http", "https"}
                and bool(parsed.hostname)
                and parsed.username is None
                and parsed.password is None
                and (parsed.port is None or parsed.port > 0)
                and not any(character.isspace() for character in seed)
            )
        except ValueError:
            valid = False
        if not valid:
            invalid_lines.append(number)

    print(f"Seed entries: {count}; invalid: {len(invalid_lines)}.")
    if invalid_lines:
        print("Fix seed lines: " + ", ".join(map(str, invalid_lines)))
        ready = False
    if count == 0:
        print("Seed file is empty or comment-only; add starting URLs before crawling.")
        ready = False
    if ready:
        print("Offline setup checks passed. Crawl permissions and targets are not checked yet.")
    return ready


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        seeds = workspace_path(args.seeds)
        data = workspace_path(args.data_dir)
        directories = [
            data,
            workspace_path(str(data / "evidence")),
            workspace_path("drafts"),
            workspace_path("logs"),
        ]
        print(f"Seeds: {seeds.relative_to(WORKSPACE)}; outputs: {data.relative_to(WORKSPACE)}.")
        print(
            f"Future crawl limits: depth={args.max_depth}, pages/seed={args.max_pages_per_seed}, "
            f"requests/run={args.max_requests}, timeout={args.request_timeout:g}s, delay={args.delay:g}s."
        )
        if args.init:
            initialize(directories, seeds)
            return 0
        return 0 if check_workspace(directories, seeds) else 1
    except ValueError as error:
        print(f"Workspace error: {error}", file=sys.stderr)
    except OSError as error:
        print(f"Workspace error: {error.strerror or 'file access failed'}. Check paths and permissions.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
