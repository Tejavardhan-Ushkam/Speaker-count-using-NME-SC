"""Layered YAML config: base.yaml <- dataset config <- method preset <- --set overrides.

Every key that can be overridden must already exist in base.yaml; an unknown key
raises, so a typo can never become a silent no-op (failure mode F).
"""

from __future__ import annotations

import copy
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "configs"


class Cfg(dict):
    """dict with recursive attribute access."""

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __deepcopy__(self, memo):
        return _wrap(copy.deepcopy(_unwrap(self), memo))


def _wrap(obj: Any) -> Any:
    if isinstance(obj, dict):
        return Cfg({k: _wrap(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [_wrap(v) for v in obj]
    return obj


def _unwrap(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _unwrap(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_unwrap(v) for v in obj]
    return obj


def deep_merge(base: dict, update: dict, strict: bool, where: str = "") -> dict:
    out = copy.deepcopy(base)
    for key, val in (update or {}).items():
        p = f"{where}.{key}" if where else key
        if strict and key not in out:
            raise KeyError(f"unknown config key {p!r} (not defined in configs/base.yaml)")
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], val, strict, p)
        else:
            out[key] = copy.deepcopy(val)
    return out


def parse_overrides(items: list[str] | None) -> dict:
    """`--set a.b=3` -> {'a': {'b': 3}} with YAML value semantics (null, lists, floats)."""
    tree: dict = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"--set expects key=value, got {item!r}")
        dotted, raw = item.split("=", 1)
        node = tree
        *parents, leaf = dotted.strip().split(".")
        for key in parents:
            node = node.setdefault(key, {})
        node[leaf] = yaml.safe_load(raw)
    return tree


def _read_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text()) or {}


def resolve_path(p: str | Path) -> Path:
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def method_path(name: str) -> Path:
    return CONFIG_DIR / "methods" / f"{name}.yaml"


def load_config(
    config: str | Path | None = None,
    method: str | None = None,
    overrides: list[str] | dict | None = None,
) -> Cfg:
    raw = _read_yaml(CONFIG_DIR / "base.yaml")
    if config is not None:
        raw = deep_merge(raw, _read_yaml(resolve_path(config)), strict=True)
    if method is not None:
        mp = method_path(method)
        if not mp.exists():
            raise FileNotFoundError(f"no method preset {mp}")
        raw = deep_merge(raw, _read_yaml(mp), strict=True)
        raw["method"]["name"] = method
    if overrides:
        tree = overrides if isinstance(overrides, dict) else parse_overrides(overrides)
        raw = deep_merge(raw, tree, strict=True)
    cfg = _wrap(raw)
    validate(cfg)
    return cfg


def validate(cfg: Cfg) -> None:
    c = cfg.clustering
    if c.laplacian not in ("unnormalized", "sym_norm"):
        raise ValueError(f"clustering.laplacian must be unnormalized|sym_norm, got {c.laplacian!r}")
    if c.backend not in ("exact", "spectralnet", "none"):
        raise ValueError(f"clustering.backend must be exact|spectralnet|none, got {c.backend!r}")
    if cfg.affinity.source not in ("ecapa", "affnet", "siamese"):
        raise ValueError(f"affinity.source must be ecapa|affnet|siamese, got {cfg.affinity.source!r}")
    if cfg.vad.source not in ("oracle", "pyannote"):
        raise ValueError(f"vad.source must be oracle|pyannote, got {cfg.vad.source!r}")
    s = cfg.segmentation
    if s.min_interval_sec < s.window_sec:
        raise ValueError("segmentation.min_interval_sec must be >= window_sec")
    if c.k_max < 1 or c.p_min < 1:
        raise ValueError("clustering.k_max and clustering.p_min must be >= 1")


def to_plain(cfg: Cfg) -> dict:
    return _unwrap(cfg)


def dump_yaml(obj: Any, p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(_unwrap(obj), sort_keys=False))


def git_commit() -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=ROOT, capture_output=True, text=True,
        ).stdout.strip()
        return sha + ("-dirty" if dirty else "")
    except Exception:  # noqa: BLE001 - no git / no commit yet
        return "unknown"


def work_dir(cfg: Cfg) -> Path:
    return ROOT / cfg.paths.work_dir / cfg.dataset.corpus / cfg.dataset.split


def results_dir(cfg: Cfg) -> Path:
    parts = [cfg.paths.results_dir, cfg.dataset.corpus, cfg.dataset.split, cfg.method.name]
    if cfg.method.tag:
        parts.append(str(cfg.method.tag))
    return ROOT.joinpath(*parts)


def write_run_metadata(cfg: Cfg, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    dump_yaml(cfg, out / "config_resolved.yaml")
    (out / "git_commit.txt").write_text(git_commit() + "\n")
