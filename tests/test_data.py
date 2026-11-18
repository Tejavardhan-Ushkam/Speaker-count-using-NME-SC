"""Segmentation rules and overlap-aware labels."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from speakercount.config import load_config
from speakercount.labels import segment_labels
from speakercount.rttm import Turn, read_rttm, rttm_path
from speakercount.segmentation import segment_intervals
from speakercount.vad import oracle_intervals

SEG = SimpleNamespace(window_sec=1.5, hop_sec=0.75, min_interval_sec=1.5, center_single_window=True)


def test_segmentation_rules():
    # 1.0 s interval dropped; 2.0 s interval -> one centred window; 3.0 s -> 3 windows; never cross gaps
    segs = segment_intervals([(0.0, 1.0), (2.0, 4.0), (10.0, 13.0)], SEG)
    assert all(s.interval_index != 0 for s in segs)
    one = [s for s in segs if s.interval_index == 1]
    assert len(one) == 1 and abs(one[0].start - 2.25) < 1e-9 and abs(one[0].end - 3.75) < 1e-9
    three = [s for s in segs if s.interval_index == 2]
    assert [round(s.start, 2) for s in three] == [10.0, 10.75, 11.5]
    assert all(s.end <= 13.0 + 1e-9 for s in three)
    # exactly 1.5 s kept
    assert len(segment_intervals([(0.0, 1.5)], SEG)) == 1


def test_oracle_union_merges_overlap():
    turns = [Turn("r", 0, 2, "A"), Turn("r", 1, 2, "B"), Turn("r", 5, 1, "A")]
    assert oracle_intervals(turns) == [(0.0, 3.0), (5.0, 6.0)]


def test_overlap_labels_synthetic():
    # A speaks 0-10, B speaks 9.9-20 (0.1 s overlap), C 30-31 overlaps A? no.
    turns = [Turn("r", 0, 10, "A"), Turn("r", 9.9, 10.1, "B"), Turn("r", 4, 1.0, "C")]
    starts = np.array([0.0, 8.5, 9.0, 9.4, 12.0, 3.5])
    ends = starts + 1.5
    clean, most, shares, spk = segment_labels(turns, starts, ends)
    assert clean[0] == "A"                 # only A
    assert clean[1] == "A"                 # A 1.5 s, B 0.1 s (6.7 %) -> still clean
    assert clean[2] is None                # A 1.0 s (67 %), B 0.6 s
    assert clean[3] is None and most[3] == "B"  # A 0.6 s, B 1.0 s
    assert clean[4] == "B"
    assert clean[5] is None and most[5] == "A"  # C overlaps A for 1.0 s
    assert shares.shape == (6, 3) and spk == ["A", "B", "C"]


def test_old_segment_counts_ami():
    """Old table: EN2002a 2243 segments, IS1009a 700 (AMI test, oracle VAD)."""
    cfg = load_config("configs/ami_test.yaml")
    from speakercount.embedding import probe_duration
    from speakercount.rttm import audio_path

    for rec, expected in (("EN2002a", 2243), ("IS1009a", 700)):
        turns = read_rttm(rttm_path(cfg, rec))
        iv = oracle_intervals(turns, probe_duration(audio_path(cfg, rec)))
        n = len(segment_intervals(iv, cfg.segmentation))
        assert n == expected, (rec, n, expected)
