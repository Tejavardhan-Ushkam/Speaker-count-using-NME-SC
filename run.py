#!/usr/bin/env python
"""Single CLI entry point for the speaker-count v2 pipeline (see README.md)."""

from __future__ import annotations

import argparse
import sys
import time


def _add_common(p: argparse.ArgumentParser, config: bool = False, method: bool = False) -> None:
    if config:
        p.add_argument("--config", required=True)
    if method:
        p.add_argument("--method", required=True)
    p.add_argument("--set", dest="overrides", action="append", default=[], metavar="dotted.key=value")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="run.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    _add_common(sub.add_parser("check-data", help="verify dataset layout, write results/data_summary.md"))
    _add_common(sub.add_parser("make-splits", help="VoxConverse dev 80/20 stratified split"))

    p = sub.add_parser("prepare", help="VAD + segment + embed (+ labels), cached")
    _add_common(p, config=True)
    p.add_argument("--force", action="store_true")
    p.add_argument("--only", nargs="*")

    _add_common(sub.add_parser("train-affnet", help="train AffinityNet"), config=True)

    p = sub.add_parser("cluster", help="cluster one split with one method")
    _add_common(p, config=True, method=True)
    p.add_argument("--only", nargs="*")
    p.add_argument("--force", action="store_true")

    _add_common(sub.add_parser("tune", help="post-processing grid search on AMI dev + Vox val"), method=True)

    p = sub.add_parser("evaluate", help="cluster + metrics + report for one split/method")
    _add_common(p, config=True, method=True)
    p.add_argument("--force", action="store_true")

    _add_common(sub.add_parser("report", help="write summary.md for one run"), config=True, method=True)
    _add_common(sub.add_parser("compare", help="write results/SUMMARY.md"))
    _add_common(sub.add_parser("plots", help="write results/plots/*"))

    p = sub.add_parser("inspect", help="print diagnostics for one recording")
    _add_common(p, config=True, method=True)
    p.add_argument("--recording", required=True)

    args = ap.parse_args(argv)
    t0 = time.time()

    if args.cmd == "check-data":
        from speakercount.datacheck import check_data

        ok = check_data()
        rc = 0 if ok else 1
    elif args.cmd == "make-splits":
        from speakercount.datacheck import make_splits

        make_splits()
        rc = 0
    elif args.cmd == "prepare":
        from speakercount.config import load_config
        from speakercount.pipeline import prepare

        prepare(load_config(args.config, overrides=args.overrides), force=args.force, only=args.only)
        rc = 0
    elif args.cmd == "train-affnet":
        from speakercount.affinity.train import train
        from speakercount.config import load_config

        train(load_config(args.config, overrides=args.overrides))
        rc = 0
    elif args.cmd in ("cluster", "evaluate"):
        from speakercount.config import load_config
        from speakercount.pipeline import cluster_split, evaluate

        cfg = load_config(args.config, method=args.method, overrides=args.overrides)
        if args.cmd == "cluster":
            cluster_split(cfg, only=args.only, force=args.force)
        else:
            evaluate(cfg, force=args.force)
        rc = 0
    elif args.cmd == "tune":
        from speakercount.tune import tune

        tune(args.method, overrides=args.overrides)
        rc = 0
    elif args.cmd == "report":
        from speakercount.config import load_config
        from speakercount.eval.report import write_report

        write_report(load_config(args.config, method=args.method, overrides=args.overrides))
        rc = 0
    elif args.cmd == "compare":
        from speakercount.eval.compare import compare

        compare()
        rc = 0
    elif args.cmd == "plots":
        from speakercount.eval.plots import make_all

        make_all()
        rc = 0
    elif args.cmd == "inspect":
        from speakercount.config import load_config
        from speakercount.pipeline import inspect

        inspect(load_config(args.config, method=args.method, overrides=args.overrides), args.recording)
        rc = 0
    else:  # pragma: no cover
        ap.error(args.cmd)
        rc = 2
    print(f"[{args.cmd}] wall time {time.time() - t0:.1f} s")
    return rc


if __name__ == "__main__":
    sys.exit(main())
