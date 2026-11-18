"""AffinityNet: output properties, loss sanity, chunked vs full inference."""

from __future__ import annotations

import numpy as np
import torch

from speakercount.affinity.data import collate
from speakercount.affinity.infer import embed_chunked, embed_full
from speakercount.affinity.loss import AffinityLoss
from speakercount.affinity.model import AffinityNet


def _session(n=3000, d=192, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((n, d)).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    t = np.sort(rng.uniform(0, 3000, n)).astype(np.float32)
    return x, t


def test_output_unit_norm_and_signed():
    torch.manual_seed(0)
    m = AffinityNet(n_layers=2).eval()
    x, t = _session(200)
    z = embed_full(m, x, t)
    assert np.allclose(np.linalg.norm(z, axis=1), 1, atol=1e-3)
    assert (z < 0).any()  # no ReLU on the output: cosines can be negative
    # alpha=0.1 residual: starts close to raw ECAPA
    assert np.mean(np.sum(z * x, axis=1)) > 0.9


def test_padding_mask_does_not_change_valid_tokens():
    torch.manual_seed(0)
    m = AffinityNet(n_layers=2, dropout=0.0).eval()
    x, t = _session(50)
    a = m(torch.tensor(x)[None], torch.tensor(t)[None])
    xp = torch.cat([torch.tensor(x), torch.randn(10, 192)])[None]
    tp = torch.cat([torch.tensor(t), torch.zeros(10)])[None]
    mask = torch.zeros(1, 60, dtype=torch.bool)
    mask[0, :50] = True
    b = m(xp, tp, mask)
    assert torch.allclose(a[0], b[0, :50], atol=1e-5)


def test_loss_prefers_separated_speakers():
    crit = AffinityLoss()
    lab = torch.tensor([[0] * 10 + [1] * 10 + [-1] * 5])
    good = torch.zeros(1, 25, 4)
    good[0, :10, 0] = 1
    good[0, 10:20, 1] = 1
    good[0, 20:, 2] = 1
    bad = torch.nn.functional.normalize(torch.randn(1, 25, 4), dim=-1)
    assert crit(good, lab)["loss"] < crit(bad, lab)["loss"]


def test_collate_masks_ambiguous_and_padding():
    x, t = _session(5)
    _, _, mask, labels = collate([(x, t, ["A", None, "B", "A", None]), (x[:2], t[:2], ["C", "C"])])
    assert labels[0].tolist() == [0, -1, 1, 0, -1] and labels[1].tolist() == [0, 0, -1, -1, -1]
    assert mask.sum() == 7


def test_chunked_vs_full_inference_close():
    if not torch.cuda.is_available():
        from tests.run_tests import skip

        skip("needs GPU")
    from speakercount.config import ROOT, load_config
    from speakercount.pipeline import emb_file, load_session

    ckpt = ROOT / "checkpoints/affnet/best.pt"
    cfg = load_config("configs/ami_test.yaml")
    if ckpt.exists() and emb_file(cfg, "EN2002c").exists():
        from speakercount.affinity.infer import load_affnet

        m = load_affnet(ckpt)                      # trained model on a real 3250-segment session
        s = load_session(cfg, "EN2002c")
        x, t = s.x, s.center
    else:
        torch.manual_seed(0)
        m = AffinityNet().cuda().eval()
        x, t = _session(3000)
    zf = embed_full(m, x, t)
    zc = embed_chunked(m, x, t, chunk=2048, stride=1024)
    cos = np.sum(zf * zc, axis=1)
    assert cos.mean() > 0.99 and cos.min() > 0.95, (cos.mean(), cos.min())
