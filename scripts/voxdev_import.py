"""Import VoxConverse dev into dataset/voxconverse/{audio,rttm}/dev and verify it.

Audio: Hugging Face mirror diarizers-community/voxconverse (Parquet; the original 16 kHz WAV bytes).
RTTM : official repo github.com/joonson/voxconverse (dev/*.rttm).
Checks: one RTTM per wav, every wav decodes, audio length covers the last RTTM turn, and the repo's
test RTTMs equal the ones already in dataset/ (same annotation version).

    python -I scripts/voxdev_import.py work/downloads/voxdev
"""
import sys
import zipfile
from pathlib import Path

import pyarrow.parquet as pq
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
src = Path(sys.argv[1]).resolve()
audio_out = ROOT / "dataset/voxconverse/audio/dev"
rttm_out = ROOT / "dataset/voxconverse/rttm/dev"
audio_out.mkdir(parents=True, exist_ok=True)
rttm_out.mkdir(parents=True, exist_ok=True)

# 1. RTTMs from the official repo zip (names checked: plain <id>.rttm only)
z = zipfile.ZipFile(src / "voxconverse_github.zip")
ends, test_same, test_diff = {}, 0, []
for name in z.namelist():
    parts = name.split("/")
    if len(parts) != 3 or not parts[2].endswith(".rttm") or not parts[2][:-5].isalnum():
        continue
    split, fn = parts[1], parts[2]
    data = z.read(name)
    if split == "dev":
        (rttm_out / fn).write_bytes(data)
        last = 0.0
        for line in data.decode().splitlines():
            f = line.split()
            if len(f) >= 5 and f[0] == "SPEAKER":
                last = max(last, float(f[3]) + float(f[4]))
        ends[fn[:-5]] = last
    elif split == "test":
        ours = ROOT / "dataset/voxconverse/rttm/test" / fn
        if ours.exists() and ours.read_bytes().split() == data.split():
            test_same += 1
        else:
            test_diff.append(fn)
print(f"dev RTTMs written: {len(ends)}; test RTTMs identical to ours: {test_same}, different: {len(test_diff)} {test_diff[:5]}")

# 2. Audio from Parquet (row group by row group to keep memory low)
written, problems = 0, []
for pf in sorted(src.glob("dev-*.parquet")):
    f = pq.ParquetFile(pf)
    for g in range(f.metadata.num_row_groups):
        col = f.read_row_group(g, columns=["audio"]).column("audio")
        for i in range(len(col)):
            a = col[i].as_py()
            rec = Path(a["path"]).stem
            if not rec.isalnum():
                problems.append(f"bad name {a['path']!r}")
                continue
            out = audio_out / f"{rec}.wav"
            out.write_bytes(a["bytes"])
            try:
                info = sf.info(out)
            except Exception as e:  # noqa: BLE001
                problems.append(f"{rec}: undecodable ({e})")
                continue
            if info.samplerate != 16000:
                problems.append(f"{rec}: sample rate {info.samplerate}")
            if rec not in ends:
                problems.append(f"{rec}: no RTTM")
            elif info.duration + 0.5 < ends[rec]:
                problems.append(f"{rec}: audio {info.duration:.1f}s shorter than RTTM end {ends[rec]:.1f}s")
            written += 1
    print(f"{pf.name}: total wav written {written}", flush=True)
missing = sorted(set(ends) - {p.stem for p in audio_out.glob("*.wav")})
print(f"wav written: {written}; RTTMs without audio: {len(missing)} {missing[:5]}")
print("PROBLEMS:" if problems else "all checks passed", *problems[:20], sep="\n  ")
sys.exit(1 if (problems or missing or test_diff) else 0)
