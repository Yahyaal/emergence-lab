# E-21 pre-registration: how do double gliders arise? (written before running)

**Question:** J-024 found 3 spontaneous double gliders (two fused Orbium-like bodies), one of
them formed by the collision of two earlier spontaneous gliders. How often do double gliders
arise from smooth starts, and how often by fusion of gliders rather than directly?

**Design:** the 8 rules of E-13/E-14 (`rule-panel-e13.txt`), smooth ell = 3 at density 0.10,
40 fresh seeds each (master seed 21), 128x128, 2000 steps. Every 10 steps: counts of
glider-sized objects (mass 55-95) and double-sized objects (mass 120-170).
Script: `scripts/double_glider_trace.py`.

**Outcomes (descriptive):** (1) worlds ending with a verified double glider (mass 120-170,
survives 1000 steps alone); (2) its origin: **fusion** if, when the double first appears
(t_d), there were >= 2 glider-sized objects for >= 100 steps before t_d and the glider count
drops by >= 2 within 30 steps of t_d; **direct** if t_d <= 100; otherwise **unclear**.
(3) worlds ending with a single glider, for comparison.

## Amendment 1 (before any E-21 run)
Testing the classifier on the J-024 example (E-19 #204, a known fusion at t ~ 530) showed that
smooth starts contain double-sized lumps at t = 0, which made t_d = 0 ("direct"). t_d is now
the start of the final uninterrupted run of double-sized objects (the double that persists to
the end). Everything else is unchanged.
