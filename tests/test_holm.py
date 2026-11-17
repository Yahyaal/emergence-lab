"""E-79 (scripts/holm_primaries.py): Holm and Benjamini-Hochberg adjusted p values on known examples."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from holm_primaries import bh, holm, holm_reject  # noqa: E402


def test_holm_and_bh_known_example():
    # Worked by hand (and as R's p.adjust gives): sorted 0.005, 0.01, 0.03, 0.04 with m = 4.
    # Holm: 4*0.005 = 0.02, 3*0.01 = 0.03, 2*0.03 = 0.06, max(0.06, 1*0.04) = 0.06.
    # BH: 4*0.005/1 = 0.02, 4*0.01/2 = 0.02, 4*0.03/3 = 0.04, 4*0.04/4 = 0.04 (running minimum from the top).
    p = [0.01, 0.04, 0.03, 0.005]
    assert holm(p) == pytest.approx([0.03, 0.06, 0.06, 0.02])
    assert bh(p) == pytest.approx([0.02, 0.04, 0.04, 0.02])


def test_holm_caps_at_one_and_is_monotone():
    p = [0.2, 0.5, 0.9, 0.001]
    adj = holm(p)
    assert adj == pytest.approx([0.6, 1.0, 1.0, 0.004])
    order = sorted(range(len(p)), key=lambda i: p[i])
    assert all(adj[order[k]] <= adj[order[k + 1]] for k in range(len(p) - 1))


def test_holm_matches_sequential_rule_and_bh_matches_scipy():
    p = [1e-6, 0.0004, 0.004, 0.012, 0.03, 0.04, 0.2, 0.7, 1.0]
    adj = holm(p)
    for alpha in (0.001, 0.01, 0.05, 0.1):
        assert [a <= alpha for a in adj] == holm_reject(p, alpha)
    scipy_stats = pytest.importorskip("scipy.stats")
    assert bh(p) == pytest.approx(list(scipy_stats.false_discovery_control(p, method="bh")))
    # BH is never more conservative than Holm
    assert all(b <= h + 1e-15 for b, h in zip(bh(p), adj))
