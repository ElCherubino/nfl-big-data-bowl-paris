"""Reproducible command line entry point with explicit failures."""
import argparse
import json
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build and validate the static RB Lifeline publication.')
    commands = parser.add_subparsers(dest='command', required=True)
    build_parser = commands.add_parser('build')
    build_parser.add_argument('--data-dir', default='nfl-data/nfl-big-data-bowl-regional-event-data/data')
    build_parser.add_argument('--output', default='outputs/site')
    build_parser.add_argument('--game-id', action='append', help='Explicitly build a smaller match scope (repeatable).')
    build_parser.add_argument('--bootstrap-replicates', type=int, default=2000)
    build_parser.add_argument('--seed', type=int, default=20261021)
    validate_parser = commands.add_parser('validate')
    validate_parser.add_argument('--output', default='outputs/site')
    validate_parser.add_argument('--check-source', action='store_true', help='Reject exports whose source fingerprint differs from the current CSV files.')
    validate_parser.add_argument('--data-dir', default='nfl-data/nfl-big-data-bowl-regional-event-data/data')
    args = parser.parse_args(argv)
    try:
        if args.command == 'build':
            from .pipeline import build
            build(args.data_dir, args.output, game_ids=args.game_id, parameters={'bootstrapReplicates': args.bootstrap_replicates, 'randomSeed': args.seed})
        else:
            from .config import CALCULATION_VERSION
            from .publish import validate_publication
            report = validate_publication(args.output)
            manifest = json.loads((Path(args.output) / 'manifest.json').read_text())
            if manifest['calculationVersion'] != CALCULATION_VERSION:
                raise ValueError('Export calculation version is stale. Regenerate with ./run --build-data.')
            if args.check_source:
                from .data import load_sources
                if load_sources(args.data_dir).fingerprint != manifest['sourceFingerprint']:
                    raise ValueError('Source CSV files changed since publication. Regenerate with ./run --build-data.')
            print(report)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'RB Lifeline: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
