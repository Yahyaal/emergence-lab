"""E-32 follow-up (J-037): the reproducer rule #970.

1. Rebuild the rule from the scan's random stream, settle the radius-13 lump, report channel masses.
2. Re-run the full lump outcome (settle + birth detector with D-030) from 3 new lumps.
3. Reduction (post hoc): the two channel-0 self-kernels as a one-channel rule, and each alone.

Usage: python scripts/e32_inspect.py      (about 40 min on one core)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import lump_scan as L  # noqa: E402
import mlenia_lump_scan as M  # noqa: E402

from emergence.physics import MultiLenia, parse_rule  # noqa: E402

REDUCED = ["MLENIA/C1/R13/T10/k0>0,r0.96,m0.109,s0.0289,h0.95,b1,1+k0>0,r0.82,m0.190,s0.0485,h0.97,b1,0.25",
           "MLENIA/C1/R13/T10/k0>0,r0.96,m0.109,s0.0289,h0.95,b1,1",
           "MLENIA/C1/R13/T10/k0>0,r0.82,m0.190,s0.0485,h0.97,b1,0.25"]


def main() -> None:
    rng = np.random.default_rng([32, 970])
    ph = MultiLenia.random(rng)
    print(ph.label())
    s, _, _ = L.settle(ph, M.mlump(ph, rng, 13))
    print("channel masses after settling", [round(float(s[c].sum()), 1) for c in range(ph.C)])
    for sd in (1, 2, 3):
        r = np.random.default_rng([3200, sd])
        o = L.outcome(ph, M.mlump(ph, r, 13), r)
        print("new lump", sd, o["settled"], o["objects"], o["verdicts"],
              [(h["verdict"], h.get("background_copies")) for h in o.get("hits", [])], flush=True)
    for lab in REDUCED:
        p = parse_rule(lab)
        for sd in (1, 2):
            r = np.random.default_rng([3300, sd])
            o = L.outcome(p, M.mlump(p, r, 13), r)
            print("reduced", lab, sd, o["settled"], o["objects"], o["verdicts"], flush=True)


if __name__ == "__main__":
    main()
