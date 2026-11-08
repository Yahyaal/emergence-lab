# E-40 pre-registration (written before running)

**Origin (Track D route 5, program soups):** Agüera y Arcas et al. (2024, "Computational Life")
report that soups of random 64-byte BFF programs, paired at random and run together on a shared
tape, undergo a "state transition" in which self-replicating programs appear and take over, with
no fitness function. Our Lenia work found movers but no reproducers (E-27 to E-32). Does
self-replication emerge from random programs in our own implementation, and does our replicator
detector (J-040, D-040) confirm it?

**Physics:** `emergence/programs/bff.py` (`Soup`, C interpreter checked against a pure-Python
reference on 300 random tapes; probes in `emergence/benchmark_programs.py`). N = 16384 programs of
L = 64 bytes, mutation 0.00024 per byte per epoch, step limit 8192 per pair (paper defaults, except
N = 2^14 rather than 2^17).

**Pilot (seeds 900-903, not in the sample):** 4 soups, 16000 epochs, interactive session
(`runs/bff/pilot-*.log`). One of four (seed 901, N = 16384) jumped at about epoch 9000 from a
high-order entropy (HOE) of 0.3 to 2.5-3.4 and stayed there; the other three stayed at 0.25-0.6
throughout. The pilot fixes the threshold below; it was not scanned with the detector.

**Design (`scripts/bff_soups.py`, commit in the experiment row):**
- 12 BFF soups, seeds 4000-4011, 16000 epochs, HOE (zlib) recorded every 250 epochs.
- Controls, 4000 epochs each, seeds 4100-4101: 2 soups in mode "noexec" (pairing and mutation,
  nothing runs: negative) and 2 in mode "copyall" (each pair's first program overwrites the
  second: deceptive for the HOE, since copying alone makes the soup repetitive).
- **Transition:** HOE >= 1.0 at a checkpoint (pilot: never above 0.65 before, never below 2.2
  after).
- **Detector:** `replicators.scan` (the 4 most common exact programs; growth test of 8 copies
  among 1024 random programs, 96 epochs without mutation; second generation; random-program
  null) on the soup 1000 epochs after its first transition checkpoint (or at the end if that
  is later than 16000) and at the end of every soup, transitioned or not. Snapshots saved as
  `runs/e40/<seed>-<epoch>.npy`.

**Primary outcome:** BFF soups containing at least one "replicator" verdict at the end.
**Predictions:** 2 to 6 of 12 soups transition (pilot 1/4); every transitioned soup contains a
verified replicator; no soup that did not transition contains one (the selection-aware null:
common programs of a random-ish soup are tested the same way); 0 replicators and 0 transitions
in noexec; copyall may raise the HOE but its verdicts are "rule-level duplication" or "no
replication", never "replicator".

**Evidence level if confirmed:** level 3 (reproduction, verified by intervention on copies, two
generations). Heredity of variation (level 4) is not tested here: it would need a measurement of
whether mutant replicators pass on their mutations, validated with its own controls.

**Limits stated in advance:** N is 8 times smaller than the paper's; 16000 epochs; 12 soups, so
the transition rate has a wide interval; the detector tests only the 4 most common exact
programs, so a soup full of many slightly different replicators could be missed (a false
negative, not a false positive); the hand-written positive control replicates only when it runs
first in a pair, unlike the paper's emergent replicators.
