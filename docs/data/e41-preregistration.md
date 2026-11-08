# E-41 pre-registration (written before running)

**Origin (J-040):** in E-40, no BFF soup of 16384 programs reached the state transition within
16000 epochs (0 of 12, against a prediction of 2 to 6 based on 1 of 4 pilot soups). The detector
was therefore never applied to a soup that had transitioned, and the primary question (do
replicators appear, and does the detector confirm them) stays open. Two follow-ups, both
decided after seeing E-40:

**A. Pilot replay.** The pilot soup seed 901 (same code, same parameters) jumped from HOE 0.3 to
2.5 at about epoch 9000. The simulation is deterministic given the seed, so re-running it must
reproduce the jump at the same epoch; the detector (`replicators.scan`, unchanged) then runs
1000 epochs after the first checkpoint with HOE >= 1.0 and at epoch 16000, as in E-40.
- **Prediction:** the jump reproduces exactly (first HOE >= 1.0 checkpoint at 9000-9250, as in
  the pilot log); at least one of the 4 most common programs is a "replicator" at both scans.
- Selection caveat: this soup was chosen *because* it transitioned. A "replicator" verdict here
  tests the detector on a real transition (a second positive control, emergent rather than
  hand-written); it says nothing about how often transitions happen.

**B. Longer runs.** E-40's 12 BFF soups continued from their epoch-16000 snapshots
(`runs/e40/bff-<seed>-16000.npy`) for 32000 more epochs (48000 in all), with fresh random streams
(seeds 5000-5011), otherwise unchanged (`scripts/bff_soups.py --e41`).
- **Prediction:** 2 to 6 of 12 transition by epoch 48000; every transitioned soup contains a
  verified replicator 1000 epochs after its transition; no soup that did not transition does.
- With 0 of 12 again, the honest statement is: in soups 8 times smaller than the paper's, the
  transition is rare within 48000 epochs (95% upper bound about 26% per soup), and the one we saw
  came from a pilot.

**Limits:** as E-40. Running B from snapshots means the "same soup" has a new random stream
from epoch 16000 on; that does not matter for the question (does the transition happen).
