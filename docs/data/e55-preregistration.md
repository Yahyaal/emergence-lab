# E-55 pre-registration (written before running)

**Origin:** all 9 replicators that emerged in our soups copy themselves backwards (mirror replicators, J-046);
only the hand-written one copies forwards. Why?

**Hypothesis (mechanism, stated before any census):** both heads start at byte 0 of the 128-byte tape. A
program can reach its partner's half backwards in one instruction: `{` moves head1 from 0 to 127 (heads wrap).
A loop such as `[{.>]` then writes byte 0 to 127, byte 1 to 126, and so on: a reversed copy of itself in its
partner, in 5 instructions. A forward copy needs head1 64 cells ahead of head0, which takes 64 `}` or a
counting loop (the hand-written replicator uses a 27-byte prefix for this). So reverse copying is far more
accessible, and the soup finds it first.

**Census (`scripts/bff_kernels.py` with its own C, the soup interpreter is untouched):** every kernel of
k = 1..6 instructions (10^k kernels each, 1,111,110 in all) is placed at bytes 0..k−1 of a 64-byte program
whose other bytes are random non-instruction filler (nonzero; one fixed filler per kernel, seeded). Each
program runs first in a pair with random partners (uniform bytes), 8192 steps, exactly as in the soup.
- **forward copier:** after the run, the partner half equals the program (≥ 60 of 64 bytes) and the program
  half is intact (≥ 60 of 64), for 4 of 4 partners; **reverse copier:** the same with the partner equal to the
  program reversed. Programs matching both are counted separately ("both").
- Screen with 1 partner, confirm with 4 (fresh).
- **Two physics:** the standard rule (head1 starts at 0) and a **counterfactual** in which head1 starts at
  byte 64 (the partner's first byte); everything else identical, same kernels and fillers.

**Primary prediction:** standard rule: reverse copiers outnumber forward copiers (summed over k) by at least
10 to 1, and the shortest reverse copier is shorter than the shortest forward one. Counterfactual: the
ordering flips (forward ≥ 10 × reverse). Both must hold for the hypothesis to pass.

**Controls:** the hand-written replicator is classified forward (standard rule); the 9 E-42 emergent
replicators are classified reverse (standard rule); 1000 uniform random programs are classified as neither;
deceptive: a program that fills its partner with one byte value (`[{.]`-style constant writer, built by hand)
and a palindromic copier (both forms identical) must not be counted as forward-only or reverse-only.

**Secondary:**
1. Filler sensitivity: repeat k ≤ 5 with filler that may contain zero bytes.
2. Mechanism trace of the 9 E-42 replicators (instrumented Python interpreter, random partners): the share
   of their partner-writing instructions (`.` at head1, `,` at head0) made while the writing head moves
   downwards, and whether head1 wraps below 0 before the first write.
3. Held-out orientation: every candidate that passes the replicator test in E-54 (its analysis JSON) is
   classified forward/reverse with the same rule. Prediction: all reverse.

**Limits:** kernels at bytes 0..k−1 only; real replicators are longer and messier, so the census measures
accessibility of the simplest copiers, not the soup's actual path. A program is only tested when it runs
first in its pair.
