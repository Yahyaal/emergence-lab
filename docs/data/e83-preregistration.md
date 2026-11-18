# E-83: when resisting parasites pays the resisting host's kin, do hosts and parasites change in a directed way? (pre-registration, written before running)

**Status:** written and committed before any confirmatory soup exists. Groundwork: J-101, D-074 (the rule), D-075 (the
instruments and design); export `docs/data/experiments/2026-11-18-e83-groundwork.json`. The rule is `scripts/bffxr.py`
(on top of `scripts/bffx.c` / `scripts/bffx.py`, unchanged); the instruments are `scripts/bffx_assay.py` (E-82's,
unchanged) and `scripts/bffxr_assay.py`; the driver is `scripts/e83_run.py`, all at commit `f1254d7`; this file is
committed alone after it. Everything run so far used pilot seeds only (1–6 and 9851–9854 for races and the seeded arm,
9801–9825 for emergence pilots, 9901–9910 for the protocol pilot, and the control seeds inside
`bffxr_assay.controls`); **the registered seeds 8401–8472 and the gate seeds 8491–8494 have never been run.**

## Question

E-82 found parasites in 40 of 40 BFF-X soups and no arms race (time-shift RQ 0.0011, interval to 0.0027 against
δ\* 0.10; host resistance 0 in 40 of 40). Its pre-registered reading: in a well-mixed soup with a read-only library, a
host that refuses callers protects a random stranger, not itself or its kin, and pays for it in bytes, so resistance
has no individual benefit. That an arms race needs a geometry where resistance pays the resister's kin was a
prediction. **In BFF-X with local structure (BFF-XR deme64, D-074), where a refusing host protects the programs around
it, most of them its kin, do hosts and parasites that arise from random code change in a directed way: do later hosts
resist earlier parasites, or later parasites exploit earlier hosts better?**

## The rule (BFF-XR, geometry deme64, D-074; fixed)

- Everything of BFF-X (D-072, libmode neighbour): a soup of W = 2^20 bytes split into programs of 4 to 128 bytes;
  each pair's tape A ++ B is run by the BFF instruction set with head0 and the instruction pointer at 0 and head1 at
  B's first byte, step limit 8192, heads halt at the ends of A ++ B; the instruction pointer runs through A and then
  through a read-only third program C's code; the tape is cut after every `!` and at 128 bytes, no piece under 4;
  mutation 0.00024 per byte per epoch. The C interpreter (`bffx.c x_epoch`) is reused unchanged.
- **The one change: who meets whom.** The programs sit on a ring in buffer order. Each epoch an offset in [0, 64) is
  drawn and the ring is cut into blocks (demes) of 64 consecutive programs. Within each block the programs are shuffled
  and paired consecutively; C is drawn uniformly from A's block (as it was before the epoch). Each pair's tape is
  written back, cut, in the block's place, so every program's pieces, including a copier's copies and a parasite's
  copies, stay within about 64 programs of where the pair was. (A pair crosses into the next block only after a block
  with an odd count; 0% of pairs are more than 64 programs apart in the control.)
- So a host's offspring sit next to it, a parasite borrows the code of a host near it, and a host that refuses
  callers protects the partners around it, most of which are its own kin. Nothing rewards copying or refusing.

## Design (fixed; code `scripts/e83_run.py`)

**Soups.** 40 primary seeds 8401–8440, each `np.random.default_rng([83, seed])`. Spares 8441–8472, used in seed order
only to replace soups excluded for not jumping, after the primary soups have finished.

**Hosts and jump** (as E-82). Every 50 epochs: the 40 most common distinct programs; a **host** copies itself into 4
of 4 random 128-byte partners with nothing to borrow (`bffx.is_copier`, libmode none). Host share = bytes held by the
families of the first 10 hosts, over W. **T** = the first checkpoint with ≥ 1 host whose checkpoint 500 epochs later
has host share ≥ 0.05. A soup with no T by epoch 10,000 is excluded.

**Samples** at S1 = T + 1,000, S2 = T + 5,000 and S3 = T + 10,000: hosts = the 5 commonest hosts; parasites = the
first 5 programs, in order of commonness among the 40 commonest non-hosts, that E-82's parasite detector
(`bffx_assay.parasite_test`, D-073; pool = 4,096 programs drawn from the snapshot, rng `[83, soup, k]`) calls
"parasite".

**Interaction scores** (E-82's). Coverage q(P, H) = the share of a random 128-byte partner that parasite P, run first,
fills with copies of itself when host H is its library (32 runs); for two samples, the mean over their 5 × 5 pairs.

**Primaries.** Unit: the soup.
- **P1 (parasites arise; a criterion):** the share of admitted soups with ≥ 1 verified parasite at each of S1, S2 and
  S3. **Pass** if ≥ 0.75. Not in the Holm family (no p value).
- **P2 (directed host–parasite change, time-shift):** RQ = mean over i < j of [q(P_j, H_i) − q(P_i, H_j)]. Positive
  when later hosts resist earlier parasites, when later parasites do better on earlier hosts, or both; swapping the
  time labels flips its sign, so the sign-flip test is the shuffled-time null.
- **P3 (host resistance):** d3 = q(P_1, H_1) − q(P_1, H_3).

P2 and P3: one-sided (positive) sign-flip permutation test over soups (Monte Carlo, 200,000 patterns,
p = (hits + 1)/(200,000 + 1)) and a 95% t interval. Undefined terms are left out as in E-82.

**Smallest effect of interest:** δ\* = 0.10 for P2 and P3, half the time-shift score of the graded built-in control
(1 of 5 later hosts is the designed resistant host: RQ 0.19 to 0.20; `bffx_assay.controls`). The instruments test
programs, not soups, so the control's value does not depend on the geometry.

**Verdicts (P2, P3):** **fail** if the upper end of the 95% interval is below δ\*; **pass** if not fail and one-sided
p < 0.05; **undecided** otherwise.

**Holm.** P2 and P3 are added to `docs/data/e79-primaries.json` with their source lines after scoring, and
`holm_primaries.py` is rerun with `--out docs/data/experiments/<date>-e83-holm51.json` (a new file; no earlier Holm
export is overwritten). P1 is entered with family "excluded". The journal says whether a pass survives.

**Predictions (for the record, from the groundwork):** P1 pass; P2 fail; P3 fail. Reason: the designed controls show
that refusal pays here (see the gate), but the cheapest resistant host found is 10 bytes against the 6-byte `[.>}]!`,
and in a designed race under this rule the resistant host is driven out by the 6-byte host within 25 epochs, with or
without parasites (D-075).

## Validation gate (before any sample is scored)

1. **Every control passes:** `bffx_assay.controls()` (16 checks, E-82's) and `bffxr_assay.controls()` (12 checks:
   ring and deme matching, conservation, local copies and local library; designed resistant, sham and plain hosts;
   coverage and protection time-shift with the designed arms race, reversed labels and the rewriting-host deceptive;
   the parasite detector on a ring soup, positive and selection-aware null). Also in `pytest` and the probe benchmark.
2. **The decisive race** (`e83_run.gate`, seeds 8491–8494): the designed resistant host R against its equal-length sham
   S (the same bytes with the trap removed, so it copies every caller), 10% of the bytes each, with 5% designed
   parasites, in random code under the E-83 rule, no mutation; resistance advantage A = [change of ln(R/S) over 50
   epochs with borrowing] − [the same with nothing borrowed, same start]. **Pass if A > 0.10 in ≥ 3 of 4 seeds**
   (pilot: 0.24, SD 0.05, 4 of 4; in E-82's well-mixed rule −0.18 at 50 epochs and −0.10 at 25).

If the gate fails, the verdict is "not testable" and nothing is scored; the soups are kept.

## Secondaries (no verdicts)

- **S1 protection.** RQ_w, the same time-shift statistic with protection w(P, H) = the share of a random 128-byte
  partner left unchanged when P runs first with H as its library. Refusal protects the partner (w ≈ 1); a host that
  copies callers with a rewritten byte lowers q without protecting anyone (w ≈ 0). A positive RQ with RQ_w ≈ 0 would
  point to rewriting, not refusal.
- **S2 resistance census:** S3 hosts that copy some S1 parasite with coverage < 0.5; host and parasite lengths; host
  turnover between S1 and S3; host share and parasite family share at S1–S3.
- **S3 the full Q and W matrices** per soup, per-soup T and trajectories; comparison with E-82 (well mixed, same
  sampler).

## Exclusions and stopping

Only soups without a confirmed jump by epoch 10,000 are excluded (and replaced from the spares). No other exclusion.
If fewer than 30 soups are admitted after the spares, every primary is reported as undecided. The run stops when all
admitted soups have reached S3 and every score is computed. No interim look at any score.

## Pilot numbers this design rests on (exploratory, pilot seeds; J-101)

- **Decisive race** (`e83_groundwork.py --compete`, seeds 1–6, no mutation; A = resistance advantage, the change of
  ln(R/S) with borrowing minus the same with nothing borrowed; mean ± SD over seeds): ring with adjacent pairs and a
  library within 4 programs +0.20 ± 0.03 at 25 epochs, +0.29 ± 0.03 at 100 (6 of 6); the same ring with the library
  drawn from the whole soup −0.01 ± 0.03; E-82's well-mixed rule −0.10 ± 0.04 at 25 epochs (later both hosts die out,
  so later horizons are floor artefacts). Demes (seeds 1–4): 16 programs +0.36 ± 0.05 at 25; **64 programs +0.22 ±
  0.07 at 25, +0.24 ± 0.05 at 50**; 256 programs −0.01 ± 0.06; 64 with a global library 0.00 ± 0.07. **Refusal pays only
  when both partner and library are local.**
- **Cost against the floor host:** R against the 6-byte `[.>}]!` (H at 20%, R at 5%, P at 5%): under deme64 R is gone by
  epoch 25 with and without borrowing (log ratio −12, the floor of the score); on the ring R falls by 2.9 in log ratio
  over 100 epochs with borrowing and by 3.6 without (benefit +0.7, cost about −3.6).
- **Shortest resistant host** (`e83_groundwork.py --search`, exhaustive over a copy loop plus up to five more bytes from
  15 values): none of 6 to 9 bytes; four of 10 bytes, `\x01-]+[.>}]!` and its variants (decrement the caller's first
  byte; an unmatched `]` halts the run unless the result is 0; restore; copy). The designed R (`\x01-[]+[.>}]!`, a
  trap instead of a halt) has 11.
- **Emergence pilot** (random code, `e83_groundwork.py --pilot`): ring with adjacent pairs, 0 of 14 soups reached host
  share 0.05 within 4,000 (10 soups) or 12,000 epochs (4); long copiers appear (first at 50 to 1,650 epochs) but a host
  front moves about one program per epoch (a seeded 768-byte block grew to 6,000 bytes in 400 epochs). The same ring
  with nothing to borrow: 3 of 4 by 12,000. Demes of 16: 0 of 5 by 6,000. **Demes of 64: 2 of 5 by 6,000**, the others
  rising. So deme64 is the smallest of the deme sizes tried in which hosts take over from random code.
- **Protocol pilot** (`e83_run.py --pilot 9901-9910`, the same code as the confirmatory driver): 9 of 10 jumped (T 3,550
  to 9,050, median 6,050; soup 9903 had no T by 10,000). **At T the shortest host was already the 6-byte `[.>}]!` in 9 of
  9 soups** (mean program length 9.5 to 11.9 bytes): under deme64 the soup shortens before hosts take over. Verified
  parasites (4-byte: `!!!!`, `.!!!`, `![.!`, ...) at all three samples in 9 of 9 (P1 share 1.0). **RQ = 0 and d3 = 0
  in 9 of 9; RQ_w = 0; every coverage value 1.0; no S3 host resists any S1 parasite.** Hosts held 5–8% of the bytes at S1
  and 10–13% at S3 (sampled hosts 6 to 8 bytes).
- **Seeded positive** (`e83_seeded.py`, seeds 9851–9854, 2,000 epochs, mutation on; 10% S, 1% R, 5% P in random code):
  under deme64 **R spread at S's expense**: from a tenth of S's bytes at epoch 0 to 0.4–0.6 of them at epoch 100, and more
  bytes than S from epoch 200–250 until both vanished, in 4 of 4. But the 6-byte `[.>}]!` arose from host debris (0 at epoch 0, 28,000
  to 42,000 bytes at epoch 100) and **R and S were gone by epoch 400–500** (R at 11,000 bytes at 500 in one soup, 0 in
  three). Under E-82's well-mixed rule R was down to 33–2,824 bytes at epoch 50 and gone by 100, S by 100. Copies of the
  key-matched parasite appeared in both geometries (a few hundred bytes at epoch 50) and did not persist. With the E-83
  sampler at epochs 100, 500 and 2,000, the time-shift statistic saw the loss of resistance: RQ −0.133 in 4 of 4 deme64
  soups (+0.133 with the time labels reversed; R was one of the five early hosts), 0 in 4 of 4 mixed soups (R was
  already gone at the first sample).
- **Noise and power.** All 9 protocol-pilot soups scored exactly 0 on P2 and P3 (SD 0). With E-82's pilot SD (0.013)
  as a conservative stand-in, the 95% interval half-width at n = 40 is about 0.004, a twenty-fifth of δ\*, and power at
  δ\* is about 1 even at the worst Holm threshold (0.05/51); 10 soups would already suffice. 40 are kept for P1's
  precision and for comparability with E-82 (same sampler, same instruments, same n).

## What each outcome will and will not mean (added before any registered seed ran)

- **Refusal pays the refuser's kin here, by construction of the geometry, and only here.** The decisive race shows a
  designed resistant host gaining on its equal-length sham under deme64 (A ≈ +0.24 over 50 epochs, 4 of 4) and not
  when the borrowed code comes from the whole soup (deme64 with a global library 0.00; demes of 256 −0.01; E-82's
  well-mixed rule −0.10 to −0.18). So E-83 tests the condition E-82's interpretation named. **A P2 or P3 fail here cannot
  be explained by "resistance has no individual or kin benefit".**
- **But the benefit is small next to the cost of the bytes a resistance check needs.** The cheapest resistant host
  found (an exhaustive search over a copy loop plus up to five extra bytes) has 10 bytes; real hosts end at the 6-byte
  `[.>}]!` (E-81, E-82). In a designed race a resistant host is driven out by the 6-byte host within 25 epochs in this
  geometry, with or without parasites; the kin benefit (+0.1 to +0.3 in log ratio) is an order of magnitude smaller
  than the length cost. **A P2 or P3 fail is therefore the expected result**, and would show that a kin benefit is not
  enough when the length floor makes resistance expensive: BFF-X's two levers (shortness and parasitism) still end in
  a host–parasite equilibrium. It would not show that kin-structured soups never sustain arms races; a substrate where
  a resistance check is cheap relative to the copy loop (longer minimal copiers, or a cost that is not length) could.
- **The long-host window is closed before T.** In E-82 hosts were long at T and shortened after it; under deme64 the
  soup shortens before hosts take over, and the shortest host at T was `[.>}]!` in 9 of 9 pilot soups. A key check
  would cost a long host relatively little, so any kin-selected resistance in this rule would have to arise before T,
  among early, rare hosts, and survive the shortening; the samples (from T + 1,000) would then still hold it. A P3
  fail together with no resistant host in any sample says it did not.
- **A P2 or P3 pass** would be the informative surprise: directed coevolution from random code. It would need a
  follow-up that names the mechanism (which bytes changed; whether the resisting hosts descend from resistant variants;
  RQ_w: refusal or rewriting) before any claim. Even then it would be **directed coevolution under one rule, not
  level 5**, which needs continuing innovation shown by a validated open-endedness measure.
- **Scope.** One rule (BFF-XR deme64: BFF-X with demes of 64 programs and a library from the caller's deme), one soup
  size, laptop scale, the E-82 instruments. Results do not transfer to the ring with adjacent pairs (where hosts did
  not take over from random code within 12,000 epochs), to smaller or larger demes, to 2D lattices, or to the consumed-
  host variant (D-072 snapshot), which was not tested here.

## Projected cost

Protocol pilot (10 soups to S3 on 10 workers, alongside 2 other jobs): 21 to 25 min per jumped soup, 10 min for a soup
without a jump. 40 primary soups on 11 workers (12 cores, `nproc`): about 4 waves, 1.7 h; with the expected 3 to 6
spares (9 of 10 jumped in the pilot) about 2 to 2.5 h; gate about 5 min; scores about 5 min. Well under 10 h.

## Launch command

```
mkdir -p runs/e83/run && systemd-inhibit --what=sleep:idle --why="E-83" setsid nohup env PYTHONPATH=.:scripts \
    python scripts/e83_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e83.json \
    > runs/e83/run/run.log 2>&1 < /dev/null &
```
