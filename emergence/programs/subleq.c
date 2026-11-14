/* SUBLEQ-family interpreter (E-75, D-054), used by subleq.py.

   A tape of N bytes (the pair's two programs) is both program and data. A program counter pc starts at 0,
   and a hidden index register r starts at 0. A rule code packs six knobs (subleq.py Rule):

     n   3 or 4 operands per instruction
     j   jump condition on the written value v (signed byte): 0 v <= 0, 1 v < 0, 2 v == 0, 3 always
     s   step added to r after every instruction: 0, +1, +2, -1
     W   operand window: a data operand x addresses pc + (x mod W) (relative mode)
     o   write offset added to the write address (0..127)
     ab  absolute mode (the published SUBLEQ): addresses x mod N, jump targets absolute

   Relative mode (r is added to the a and b addresses only; c is a fixed relative address):
     n = 3:  A = pc + a%W + o + r, B = pc + b%W + r;      t[A] -= t[B];         target = pc + (int8)c
     n = 4:  A = pc + a%W + o + r, B = pc + b%W + r, C = pc + c%W;
             t[A] = t[B] - t[C];                                               target = pc + (int8)d
   Absolute mode: the same with pc dropped from data addresses and target = c (n = 3) or d (n = 4).
   All addresses are taken mod N. If the condition holds pc = target, else pc += n. Execution stops after
   max_steps instructions, or when an instruction would read past either end of the tape. */
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

static const int SV[4] = {0, 1, 2, -1};
static const int WV[8] = {128, 64, 32, 16, 8, 128, 128, 128};

typedef struct { int n, j, s, W, o, ab; } rule_t;

static rule_t dec(int code) {
    rule_t r;
    r.n = (code & 1) ? 4 : 3;
    r.j = (code >> 1) & 3;
    r.s = SV[(code >> 3) & 3];
    r.W = WV[(code >> 5) & 7];
    r.o = (code >> 8) & 127;
    r.ab = (code >> 15) & 1;
    return r;
}

static inline int md(int x, int N) { x %= N; return x < 0 ? x + N : x; }

static long run(uint8_t *t, int N, long max_steps, int code) {
    rule_t R = dec(code);
    int pc = 0, reg = 0;
    long steps = 0;
    while (steps < max_steps) {
        if (pc < 0 || pc + R.n > N) break;
        int a = t[pc], b = t[pc + 1], c = t[pc + 2], d = R.n == 4 ? t[pc + 3] : c;
        int A, B, target;
        uint8_t v;
        if (R.ab) {
            A = md(a + R.o + reg, N);
            B = md(b + reg, N);
        } else {
            A = md(pc + a % R.W + R.o + reg, N);
            B = md(pc + b % R.W + reg, N);
        }
        if (R.n == 3) {
            v = (uint8_t)(t[A] - t[B]);
        } else {
            int C = R.ab ? md(c, N) : md(pc + c % R.W, N);
            v = (uint8_t)(t[B] - t[C]);
        }
        t[A] = v;
        if (R.ab) target = d;
        else target = pc + (int8_t)d;
        int8_t sv = (int8_t)v;
        int jump = R.j == 0 ? sv <= 0 : R.j == 1 ? sv < 0 : R.j == 2 ? sv == 0 : 1;
        pc = jump ? target : pc + R.n;
        reg = md(reg + R.s, N);
        steps++;
    }
    return steps;
}

long sq_run(uint8_t *tape, int n, long max_steps, int code) { return run(tape, n, max_steps, code); }

/* One epoch: as bff_epoch (mode 0 run, 1 no execution, 2 copy-all). */
long sq_epoch(uint8_t *soup, int L, const int32_t *pairs, int npairs, long max_steps, int mode, int code) {
    uint8_t tape[1024];
    long total = 0;
    if (2 * L > 1024) return -1;
    for (int p = 0; p < npairs; p++) {
        uint8_t *a = soup + (long)pairs[2 * p] * L, *b = soup + (long)pairs[2 * p + 1] * L;
        if (mode == 1) continue;
        if (mode == 2) { for (int i = 0; i < L; i++) b[i] = a[i]; continue; }
        for (int i = 0; i < L; i++) { tape[i] = a[i]; tape[L + i] = b[i]; }
        total += run(tape, 2 * L, max_steps, code);
        for (int i = 0; i < L; i++) { a[i] = tape[i]; b[i] = tape[L + i]; }
    }
    return total;
}

static uint64_t sm(uint64_t *s) {
    uint64_t z = (*s += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

/* Shift-aware copy test, as bff_kernels classify_shift: run p + random partner `partners` times; the program
   half must stay intact in >= thr bytes, and one shift d (|d| <= maxshift; forward or mirrored) must match
   >= overlap - (L - thr) bytes with every partner. Returns orientation bits (1 forward, 2 mirrored); *shift
   = d; `copy` (if not NULL) receives the partner half of the first run. */
static int copier(const uint8_t *p, int L, int code, int partners, uint64_t s, long max_steps, int thr,
                  int maxshift, int8_t *shift, uint8_t *copy) {
    uint8_t tape[1024], okf[129], okr[129];
    int slack = L - thr, nd = 2 * maxshift + 1, alive = 1;
    for (int k = 0; k < nd; k++) okf[k] = okr[k] = 1;
    for (int q = 0; q < partners && alive; q++) {
        memcpy(tape, p, L);
        for (int j = 0; j < L; j++) tape[L + j] = (uint8_t)sm(&s);
        run(tape, 2 * L, max_steps, code);
        if (q == 0 && copy) memcpy(copy, tape + L, L);
        int intact = 0;
        for (int j = 0; j < L; j++) intact += tape[j] == p[j];
        if (intact < thr) return 0;
        alive = 0;
        for (int k = 0; k < nd; k++) {
            int d = k - maxshift, ov = L - (d < 0 ? -d : d), f = 0, r = 0;
            for (int j = 0; j < L; j++) {
                int src = j - d;
                if (src < 0 || src >= L) continue;
                f += tape[L + j] == p[src];
                r += tape[L + j] == p[L - 1 - src];
            }
            if (f < ov - slack) okf[k] = 0;
            if (r < ov - slack) okr[k] = 0;
            alive |= okf[k] | okr[k];
        }
    }
    if (!alive) return 0;
    int fw = -999, rv = -999;
    for (int k = 0; k < nd; k++) {
        int d = k - maxshift;
        if (okf[k] && (fw == -999 || abs(d) < abs(fw))) fw = d;
        if (okr[k] && (rv == -999 || abs(d) < abs(rv))) rv = d;
    }
    *shift = (int8_t)(fw != -999 ? fw : (rv != -999 ? rv : 0));
    return (fw != -999) | ((rv != -999) << 1);
}

/* D-055 (proposed) copy test: copier() and, if guard, the functional guard: the first partner's copy must
   itself be a copier (same test, fresh partners). */
void sq_classify(const uint8_t *progs, int nprog, int L, int code, int partners, uint64_t seed, long max_steps,
                 int thr, int maxshift, int guard, uint8_t *out, int8_t *shift) {
    uint8_t cp[512];
    for (int i = 0; i < nprog; i++) {
        uint64_t s = seed ^ (0xD1B54A32D192ED03ull * (uint64_t)(i + 1));
        int8_t sh = 0, sh2 = 0;
        int o = copier(progs + (long)i * L, L, code, partners, s, max_steps, thr, maxshift, &sh, cp);
        if (o && guard && !copier(cp, L, code, partners, s ^ 0x5bd1e995ull, max_steps, thr, maxshift, &sh2, NULL))
            o = 0;
        out[i] = (uint8_t)o;
        shift[i] = o ? sh : 0;
    }
}

/* E-75 phase 1 census pre-filter: nprog random programs (L bytes) each run once with a random partner (max_steps).
   A program is a hit if some m-byte block of it (as it was before the run) appears anywhere in the partner half
   afterwards. Hits are written to hits (maxhits x L bytes); returns the number of hits (may exceed maxhits). */
long sq_census(int code, long nprog, int L, uint64_t seed, long max_steps, int m, uint8_t *hits, long maxhits) {
    uint8_t p[512], tape[1024];
    uint64_t pb[512], qb[512];
    long nh = 0;
    uint64_t s = seed;
    if (m > 8 || m < 1 || 2 * L > 1024) return -1;
    uint64_t mask = m == 8 ? ~0ull : ((1ull << (8 * m)) - 1);
    int nb = L - m + 1;
    for (long i = 0; i < nprog; i++) {
        for (int j = 0; j < L; j += 8) { uint64_t z = sm(&s); memcpy(p + j, &z, 8); }
        for (int j = 0; j < L; j += 8) { uint64_t z = sm(&s); memcpy(tape + L + j, &z, 8); }
        memcpy(tape, p, L);
        run(tape, 2 * L, max_steps, code);
        for (int j = 0; j < nb; j++) {
            uint64_t x = 0, y = 0;
            memcpy(&x, p + j, m);
            memcpy(&y, tape + L + j, m);
            pb[j] = x & mask;
            qb[j] = y & mask;
        }
        int hit = 0;
        for (int a = 0; a < nb && !hit; a++)
            for (int b = 0; b < nb; b++)
                if (pb[a] == qb[b]) { hit = 1; break; }
        if (hit) {
            if (nh < maxhits) memcpy(hits + nh * L, p, L);
            nh++;
        }
    }
    return nh;
}

/* E-75 phase 3 predictor census (D-057): as sq_census, but each program is `period` random bytes repeated to L
   (period = L gives sq_census's random programs). Also counts runs that halt within `halt_k` steps (*nhalt):
   the freezing risk. Program and partner come from the same splitmix stream as sq_census. */
long sq_census_p(int code, long nprog, int L, uint64_t seed, long max_steps, int m, int period, int halt_k,
                 uint8_t *hits, long maxhits, long *nhalt) {
    uint8_t p[512], tape[1024];
    uint64_t pb[512], qb[512];
    long nh = 0, nhl = 0;
    uint64_t s = seed;
    if (m > 8 || m < 1 || 2 * L > 1024 || period < 1 || period > L) return -1;
    uint64_t mask = m == 8 ? ~0ull : ((1ull << (8 * m)) - 1);
    int nb = L - m + 1;
    for (long i = 0; i < nprog; i++) {
        for (int j = 0; j < period; j += 8) { uint64_t z = sm(&s); memcpy(p + j, &z, period - j < 8 ? period - j : 8); }
        for (int j = period; j < L; j++) p[j] = p[j % period];
        for (int j = 0; j < L; j += 8) { uint64_t z = sm(&s); memcpy(tape + L + j, &z, 8); }
        memcpy(tape, p, L);
        long st = run(tape, 2 * L, max_steps, code);
        if (st <= halt_k) nhl++;
        for (int j = 0; j < nb; j++) {
            uint64_t x = 0, y = 0;
            memcpy(&x, p + j, m);
            memcpy(&y, tape + L + j, m);
            pb[j] = x & mask;
            qb[j] = y & mask;
        }
        int hit = 0;
        for (int a = 0; a < nb && !hit; a++)
            for (int b = 0; b < nb; b++)
                if (pb[a] == qb[b]) { hit = 1; break; }
        if (hit) {
            if (nh < maxhits) memcpy(hits + nh * L, p, L);
            nh++;
        }
    }
    *nhalt = nhl;
    return nh;
}

/* E-75 phase 6 product census (D-061): does a random pair's run WRITE a replicator?
   Pre-filter for one candidate program x (L bytes): `lin` lineages, each running x with a fresh random partner,
   then that partner half with a fresh random partner, for `gens` generations. x passes if some m-byte block of x
   that is not one repeated byte (skip_const) is found in the partner half after every generation of >= need
   lineages (a lineage stops at the first generation with none).
   This is a cheap version of the inheritance test (inherit.py: 5 generations, 3 of 4 lineages, then a
   knockout), whose positives are then confirmed in Python. */
static inline uint32_t bh(uint64_t v) { return (uint32_t)((v * 0x9E3779B97F4A7C15ull) >> 52); } /* 12 bits */

static int has_block(const uint8_t *cur, int nb, int m, uint64_t mask, const uint64_t *xb, int nx,
                     const uint64_t *bloom) {
    for (int b = 0; b < nb; b++) {
        uint64_t y = 0;
        memcpy(&y, cur + b, m);
        y &= mask;
        uint32_t h = bh(y);
        if (!(bloom[h >> 6] >> (h & 63) & 1)) continue;
        for (int a = 0; a < nx; a++)
            if (xb[a] == y) return 1;
    }
    return 0;
}

static int prefilter(const uint8_t *x, int L, int code, uint64_t *s, long max_steps, int m, int gens, int lin,
                     int need, int skip_const) {
    uint8_t tape[1024], cur[512];
    uint64_t xb[512], bloom[64];
    int nb = L - m + 1, ok = 0, nx = 0;
    uint64_t mask = m == 8 ? ~0ull : ((1ull << (8 * m)) - 1);
    memset(bloom, 0, sizeof bloom);
    for (int j = 0; j < nb; j++) {
        if (skip_const) {
            int c = 1;
            for (int k = 1; k < m; k++) c &= x[j + k] == x[j];
            if (c) continue;
        }
        uint64_t v = 0;
        memcpy(&v, x + j, m);
        v &= mask;
        xb[nx++] = v;
        uint32_t h = bh(v);
        bloom[h >> 6] |= 1ull << (h & 63);
    }
    if (!nx) return 0;
    for (int l = 0; l < lin; l++) {
        memcpy(cur, x, L);
        int found = 1;
        for (int g = 0; g < gens && found; g++) {
            memcpy(tape, cur, L);
            for (int j = 0; j < L; j += 8) { uint64_t z = sm(s); memcpy(tape + L + j, &z, 8); }
            run(tape, 2 * L, max_steps, code);
            memcpy(cur, tape + L, L);
            found = has_block(cur, nb, m, mask, xb, nx, bloom); /* a block absent after any generation fails */
        }
        ok += found;
        if (ok >= need) return 1;
        if (ok + (lin - l - 1) < need) return 0;
    }
    return ok >= need;
}

long sq_prefilter(const uint8_t *progs, int nprog, int L, int code, uint64_t seed, long max_steps, int m, int gens,
                  int lin, int need, int skip_const, uint8_t *out) {
    uint64_t s = seed;
    long n = 0;
    if (m > 8 || m < 1 || 2 * L > 1024) return -1;
    for (int i = 0; i < nprog; i++) {
        out[i] = (uint8_t)prefilter(progs + (long)i * L, L, code, &s, max_steps, m, gens, lin, need, skip_const);
        n += out[i];
    }
    return n;
}

/* Product census: npairs random pairs (A, B), each run once (max_steps) as in a soup. Each half of the result that
   differs from its input is a *product*; products passing the pre-filter are hits. hits receives up to maxhits
   rows of 3L bytes: the product, then the input pair (A, B); side[k] = 0 (A's half, rewritten by its own run) or
   1 (B's half, written by A). stats[0] = products, stats[1] = total steps of the pair runs, stats[2] = pair
   runs reaching max_steps. Returns the number of hits (may exceed maxhits). */
long sq_products(int code, long npairs, int L, uint64_t seed, long max_steps, int m, int gens, int lin, int need,
                 int skip_const, uint8_t *hits, uint8_t *side, long maxhits, long *stats) {
    uint8_t in[1024], tape[1024];
    uint64_t s = seed, s2 = seed ^ 0x6a09e667f3bcc909ull;
    long nh = 0, np = 0, st = 0, nmax = 0;
    if (m > 8 || m < 1 || 2 * L > 1024) return -1;
    for (long i = 0; i < npairs; i++) {
        for (int j = 0; j < 2 * L; j += 8) { uint64_t z = sm(&s); memcpy(in + j, &z, 8); }
        memcpy(tape, in, 2 * L);
        long k = run(tape, 2 * L, max_steps, code);
        st += k;
        nmax += k >= max_steps;
        for (int h = 0; h < 2; h++) {
            if (!memcmp(tape + h * L, in + h * L, L)) continue;
            np++;
            if (prefilter(tape + h * L, L, code, &s2, max_steps, m, gens, lin, need, skip_const)) {
                if (nh < maxhits) {
                    memcpy(hits + nh * 3 * L, tape + h * L, L);
                    memcpy(hits + nh * 3 * L + L, in, 2 * L);
                    side[nh] = (uint8_t)h;
                }
                nh++;
            }
        }
    }
    stats[0] = np;
    stats[1] = st;
    stats[2] = nmax;
    return nh;
}

/* Soup-material product census (E-75 phase 8): as sq_products, but each pair (A, B) is two distinct programs drawn
   at random from `soup` (nprog x L) instead of fresh random bytes. The soup is not modified. */
long sq_products_from(int code, const uint8_t *soup, long nprog, long npairs, int L, uint64_t seed, long max_steps,
                      int m, int gens, int lin, int need, int skip_const, uint8_t *hits, uint8_t *side,
                      long maxhits, long *stats) {
    uint8_t in[1024], tape[1024];
    uint64_t s = seed, s2 = seed ^ 0x6a09e667f3bcc909ull;
    long nh = 0, np = 0, st = 0, nmax = 0;
    if (m > 8 || m < 1 || 2 * L > 1024 || nprog < 2) return -1;
    for (long i = 0; i < npairs; i++) {
        long a = (long)(sm(&s) % (uint64_t)nprog), b;
        do { b = (long)(sm(&s) % (uint64_t)nprog); } while (b == a);
        memcpy(in, soup + a * L, L);
        memcpy(in + L, soup + b * L, L);
        memcpy(tape, in, 2 * L);
        long k = run(tape, 2 * L, max_steps, code);
        st += k;
        nmax += k >= max_steps;
        for (int h = 0; h < 2; h++) {
            if (!memcmp(tape + h * L, in + h * L, L)) continue;
            np++;
            if (prefilter(tape + h * L, L, code, &s2, max_steps, m, gens, lin, need, skip_const)) {
                if (nh < maxhits) {
                    memcpy(hits + nh * 3 * L, tape + h * L, L);
                    memcpy(hits + nh * 3 * L + L, in, 2 * L);
                    side[nh] = (uint8_t)h;
                }
                nh++;
            }
        }
    }
    stats[0] = np;
    stats[1] = st;
    stats[2] = nmax;
    return nh;
}
