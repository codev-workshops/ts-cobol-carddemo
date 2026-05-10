#!/usr/bin/env python3
"""Orchestrator – run all ETL loaders in dependency order.

Usage:
    python load_all.py              # load all tables
    python load_all.py --validate   # load + validate
"""

import argparse
import importlib
import sys

from etl_common import logger

LOADERS = [
    "load_acctdata",
    "load_carddata",
    "load_cardxref",
    "load_custdata",
    "load_discgrp",
    "load_tcatbal",
    "load_trancatg",
    "load_trantype",
]


def main():
    parser = argparse.ArgumentParser(description="CardDemo seed data loader")
    parser.add_argument(
        "--validate", action="store_true", help="Run validation after loading"
    )
    args = parser.parse_args()

    failures = []
    for name in LOADERS:
        logger.info("=== Running %s ===", name)
        try:
            mod = importlib.import_module(name)
            mod.main()
        except Exception as exc:
            logger.error("%s FAILED: %s", name, exc)
            failures.append(name)

    if failures:
        logger.error("Failed loaders: %s", ", ".join(failures))
        sys.exit(1)

    logger.info("All loaders completed successfully")

    if args.validate:
        logger.info("=== Running validation ===")
        import validate
        validate.main()


if __name__ == "__main__":
    main()
